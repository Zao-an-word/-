from fastapi import Depends,  UploadFile, File, HTTPException, Form, Body, APIRouter
from httpx import TimeoutException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from ....db.session import get_db
from fastapi.responses import JSONResponse
from ....domains.users.models import User
from ....services.auth_service import (
    get_current_active_user,
    MapGenerator,
)
from ....domains.novels.schemas import MapGenerateRequest
from ....domains.conversations.models import Conversations
import os
from ....core.config import Config

router = APIRouter()

#地图生成（用户认证）
@router.post("/generate-map", response_model=dict)
async def generate_map_endpoint(
        request: MapGenerateRequest = Body(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    try:
        text = request.text
        conversation_uuid = request.conversation_uuid
        # 验证用户是否活跃
        if not current_user:
            raise HTTPException(status_code=400, detail="请使用活跃账号登录")

        # 1. 验证对话是否存在且属于当前用户
        result = await db.execute(
            select(Conversations).filter(
                Conversations.uuid == conversation_uuid,
                Conversations.user_id == current_user.id
            )
        )
        conversation = result.scalars().first()

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"对话 {conversation_uuid} 不存在或用户无权操作"
            )

        # 2. 生成地图
        mapconfig = Config()
        map_generator =MapGenerator(mapconfig)
        file_path = await map_generator.generate_map(text)
        map_url = f"http://127.0.0.1:8000/static{file_path.replace(os.sep, '/')}"

        # 3. 更新该对话的map_url（确保只更新当前对话的最后一次生成结果）
        conversation.map_url = map_url
        conversation.status = 1
        conversation.updated_at = datetime.now()  # 更新时间戳
        await db.commit()
        await db.refresh(conversation)  # 刷新会话中的对象

        return JSONResponse(content={
            "map_url": map_url,
            "conversation_id": conversation_uuid,  # 返回关联的对话ID
            "user_id": current_user.id,
            "message": f"地图生成成功，已更新对话 {conversation_uuid} 的地图URL"
        })

    except TimeoutException:
        raise HTTPException(status_code=504, detail="请求超时，请稍后再试")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"地图生成失败：{str(e)}")

@router.post("/get_photo")
async def get_history(uuid: str, db: AsyncSession = Depends(get_db)):
        stmt = select(Conversations).where(Conversations.uuid == uuid)
        result = await db.execute(stmt)
        history = result.scalars().first()
        response = {
            "url1": None,
            "url2": None,
            "url3": None
        }

        # 仅当 history 存在时才赋值
        if history is not None:
            response["url1"] = history.map_url  # 地图 URL
            response["url2"] = history.peo_url  # 人物关系图 URL
            response["url3"] = history.photo_url  # 文生图 URL
        else:
            # 可选：打印日志提示未找到记录，方便调试
            print(f"未找到 uuid 为 {uuid} 的对话记录")
        return response
