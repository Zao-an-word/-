from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import shutil
from ....db.session import get_db
from ....services.auth_service import (
    get_current_active_user,
    get_all_novels_with_author,
    generate_novel_introduction
)
from ....domains.users.models import User
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ....domains.novels.schemas import NovelResponse, NovelCreate, NovelUploadParams
from sqlalchemy.future import select
from ....domains.novels.models import Novels

# 加载环境变量
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

import logging
# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
class LoginRequest(BaseModel):
    username: str
    password: str
# 创建数据库表

# 创建路由实例（前缀为/auth，标签用于文档分类）
router = APIRouter()


# 配置封面存储路径
COVER_UPLOAD_DIR = "static/covers"
os.makedirs(COVER_UPLOAD_DIR, exist_ok=True)  # 确保目录存在

# 路由，获取所有小说信息（包含作者名等）
@router.get("/novels", response_model=List[NovelResponse])
async def read_all_novels(db: AsyncSession = Depends(get_db)):
    novels = await get_all_novels_with_author(db)
    return novels


# 1. 上传小说（需登录，且自动关联当前用户ID）
# 4. 上传小说接口（修改参数接收方式）
@router.post("/novels", response_model=NovelResponse)
async def create_novel(
        # 从请求体获取所有参数（合并NovelCreate和NovelUploadParams）
        novel_data: NovelCreate,
        upload_params: NovelUploadParams,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    try:
        # 1. 验证prompt不为空（防止前端验证失效）
        if not upload_params.prompt.strip():
            raise HTTPException(status_code=400, detail="小说内容不能为空")

        # 2. 生成简介（AI逻辑）
        ai_introduction = generate_novel_introduction(upload_params.prompt)

        # 3. 创建小说记录（确保content不为空）
        db_novel = Novels(
            title=novel_data.title,
            introduction=ai_introduction,
            cover_url=novel_data.cover_url,
            status=novel_data.status,
            user_id=current_user.id,
            content=upload_params.prompt,  # 使用请求体中的prompt作为内容
            tags=upload_params.prompt_tags,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(db_novel)
        await db.commit()
        await db.refresh(db_novel)

        # 4. 构造响应数据
        return {
            **db_novel.__dict__,
            "author_name": current_user.username
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建小说失败: {str(e)}")

# @router.get("/novels/{novel_id}")
# async def get_novel_detail(novel_id: int, db: AsyncSession = Depends(get_db)):
#     stmt = select(Novels).where(Novels.id == novel_id)
#     result = await db.execute(stmt)
#     novel = result.scalar_one_or_none()
#
#     if not novel:
#         raise HTTPException(status_code=404, detail="Novel not found")
#
#     return novel
@router.get("/novels/{novel_id}")
async def get_novel_detail(novel_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Novels, User.username).join(User).where(Novels.id == novel_id)
    result = await db.execute(stmt)
    novel_data = result.first()

    if not novel_data:
        raise HTTPException(status_code=404, detail="Novel not found")

    novel, author_name = novel_data
    # 转换为字典并添加作者名称
    novel_dict = novel.__dict__
    novel_dict["author_name"] = author_name
    # 移除SQLAlchemy内部属性
    novel_dict.pop("_sa_instance_state", None)

    return novel_dict

# 2. 上传封面图片（需登录）
@router.post("/novels/cover")
async def upload_cover(
        novel_id: int,  # 需要关联的小说ID
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    try:
        # 1. 验证小说是否存在且属于当前用户
        result = await db.execute(
            select(Novels).filter(
        Novels.id == novel_id,
                Novels.user_id == current_user.id  # 确保是当前用户的小说
            )
        )
        db_novel = result.scalar_one_or_none()

        if not db_novel:
            raise HTTPException(
                status_code=404,
                detail="小说不存在或无权操作"
            )

        # 2. 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/gif"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="只允许上传JPG、PNG、GIF格式的图片"
            )

        # 3. 生成唯一文件名（避免冲突）
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{current_user.id}_{file.filename}"
        file_path = os.path.join(COVER_UPLOAD_DIR, filename)

        # 4. 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 5. 生成可访问的URL并更新到novels表
        cover_url = f"http://127.0.0.1:8000/static{file_path.replace(os.sep, '/').lstrip('static')}"
        db_novel.cover_url = cover_url  # 更新小说的封面地址
        db_novel.updated_at = datetime.now()  # 更新时间戳
        await db.commit()
        await db.refresh(db_novel)

        return {
            "cover_url": cover_url,
            "message": "封面上传并关联成功",
            "novel_id": novel_id  # 返回关联的小说ID
        }

    except Exception as e:
        await db.rollback()  # 出错时回滚数据库操作
        logger.error(f"Database error: {str(e)}")  # 记录日志
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

