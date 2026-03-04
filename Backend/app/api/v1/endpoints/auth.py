from datetime import datetime, timedelta
import pytz
from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File,Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from starlette.responses import JSONResponse

from ....db.session import get_db
from ....services.auth_service import (
    get_user_by_username,
    create_user,
    authenticate_user,
    get_online_users_count,
    get_total_users_count,
    get_usage_peak_hours,
    update_user_profile,
    get_current_active_user,
    allowed_file,
    save_file,
    get_image_preview,
    extract_text
)

from ....domains.users.schemas import UserResponse, AdminStats, UserCreate, Token,UserProfileUpdate,ChangePasswordRequest
from ....domains.users.models import User

from sqlalchemy import select
from ....core.security import verify_password,get_password_hash,create_access_token
from ....core.config import   MAX_FILE_SIZE, ALLOWED_EXTENSIONS, UPLOAD_DIR, \
    ALLOWED_IMAGE_TYPES, ALLOWED_TEXT_TYPES, FILE_URL
from typing import List
import uuid


# 加载环境变量
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# 头像保存路径（确保目录存在）
AVATAR_UPLOAD_DIR = "static/avatars"
os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)

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

# 路由：用户注册
@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    return await create_user(db=db, user=user)

# 路由：用户登录
@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # 判断请求体格式
    if "application/x-www-form-urlencoded" in request.headers.get("content-type", ""):
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
    else:
        json_data = await request.json()
        username = json_data.get("username")
        password = json_data.get("password")
    user = await authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码不正确")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    user.last_login_at = datetime.now(pytz.utc)
    user.status = 1
    await db.commit()

    return {"access_token": access_token, "token_type": "bearer", "role": user.role}


# 路由：获取当前用户信息
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
@router.get("/me")
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    try:
        # 确保返回的字段与前端预期一致
        return {
            "id": current_user.id,
            "username": current_user.username,
            "avatar_url": current_user.avatar_url,  # 若字段名不同需修改
            "mailbox": current_user.mailbox,
            "phone": current_user.phone,
            "gender": current_user.gender,
            "birthday": current_user.birthday,
            "created_at": current_user.created_at
        }
    except Exception as e:
        # 捕获并打印所有异常
        print(f"/api/me 接口错误: {str(e)}")
        raise  # 重新抛出，让FastAPI返回500并包含错误信息

#用户更新
@router.put("/profile", response_model=UserResponse)
async def update_profile(
        profile_update: UserProfileUpdate,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    # 打印请求数据
    logger.debug(f"收到更新请求: {profile_update.dict()}")
    logger.debug(f"当前用户ID: {current_user.id}, 用户名: {current_user.username}")

    # 手机号查重逻辑
    if profile_update.phone:
        logger.debug(f"检查手机号: {profile_update.phone} 是否已被占用")
        result = await db.execute(select(User).where(User.phone == profile_update.phone))
        existing_user = result.scalars().first()

        if existing_user:
            logger.debug(f"找到手机号所有者: ID={existing_user.id}, 用户名={existing_user.username}")
            if existing_user.id != current_user.id:
                logger.warning(f"手机号 {profile_update.phone} 已被用户 {existing_user.username} 注册")
                raise HTTPException(status_code=400, detail="手机号已被注册")
        else:
            logger.debug(f"手机号 {profile_update.phone} 未被占用，可以使用")

    # 执行更新前打印
    logger.debug(f"即将更新用户 {current_user.username} 的信息: {profile_update.dict(exclude_unset=True)}")
    updated_user = await update_user_profile(db, user=current_user, profile_update=profile_update)

    # 返回前打印更新结果
    logger.debug(f"用户信息更新成功: ID={updated_user.id}, 新手机号={updated_user.phone}")
    return updated_user

# 路由：用户退出登录
@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    # 设置为离线状态
    current_user.status = 0  # 0表示离线
    await db.commit()
    return {"message": "退出登录成功"}


# 管理员路由：获取统计信息
@router.get("/admin/stats", response_model=AdminStats)
async def get_admin_stats(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    # 检查用户是否为管理员
    if current_user.role != 1:
        raise HTTPException(status_code=403, detail="权限不足")

    # 获取统计数据
    online_count = await get_online_users_count(db)
    total_count = await get_total_users_count(db)
    peak_hours = await get_usage_peak_hours(db)

    return {
        "online_users_count": online_count,
        "total_users_count": total_count,
        "usage_peak_hours": peak_hours
    }


#更新头像url
@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # 获取当前登录用户
):
    # 1. 验证文件类型（仅允许图片）
    allowed_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="仅支持JPG、PNG、GIF格式的图片"
        )

    # 2. 生成唯一文件名（避免重复）
    file_ext = file.filename.split(".")[-1].lower()  # 获取文件扩展名
    unique_filename = f"avatar_{uuid.uuid4()}.{file_ext}"  # 生成唯一文件名
    file_path = os.path.join(AVATAR_UPLOAD_DIR, unique_filename)

    # 3. 保存文件到本地
    with open(file_path, "wb") as buffer:
        content = await file.read()  # 异步读取文件内容
        buffer.write(content)

    # 4. 构建可访问的URL（根据实际部署地址调整）
    avatar_url = f"http://localhost:8000/static/avatars/{unique_filename}"

    # 5. 更新用户表的avatar_url字段
    current_user.avatar_url = avatar_url
    current_user.updated_at = datetime.now()  # 更新时间戳
    await db.commit()  # 提交事务
    await db.refresh(current_user)  # 刷新用户实例

    return JSONResponse({
        "success": True,
        "avatar_url": avatar_url,
        "message": "头像上传成功"
    })




@router.post("/modify-password", status_code=status.HTTP_200_OK)
async def change_password(
        request: ChangePasswordRequest,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        # 1. 验证旧密码是否正确
        if not verify_password(request.old_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码不正确"
            )

        # 2. 验证新密码是否与旧密码相同
        if verify_password(request.new_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码不能与旧密码相同"
            )

        # 3. 更新密码
        current_user.password_hash = get_password_hash(request.new_password)
        current_user.updated_at = datetime.now()  # 更新时间戳
        await db.commit()
        await db.refresh(current_user)

        return {"message": "密码修改成功，请重新登录"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改失败：{str(e)}"
        )


