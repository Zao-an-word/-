from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from ....db.session import get_db
from ....domains.conversations.models import Conversations
from ....domains.chat.schemas import ChatRequest,MultiAgentChatAssistant
from sqlalchemy import select, delete, update
from ....services.assign_port import assign_port
from ....domains.messages.models import Messages
from fastapi import Depends
from ....services.auth_service import get_current_active_user
from ....domains.users.models import User
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


@router.post("/get_port")
async def get_port(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    port = await assign_port(db,current_user=current_user)
    return {"port": port}


@router.post("/get_history")
async def get_history(uuid: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Messages).where(Messages.uuid == uuid)
    result = await db.execute(stmt)
    history = result.scalars().all()

    response = []
    for i in history:
        response.append({
            "content": i.content,
            "isUser": i.role == "user",
            "timestamp": i.time
        })

    return {"result": response}


@router.post("/get_conversations")
async def get_history(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    user_id = current_user.id
    print(user_id)
    stmt = select(Conversations).where(Conversations.user_id == user_id)
    result = await db.execute(stmt)
    conversations = result.scalars().all()
    num = 1
    response = []
    for i in conversations:
        response.append({
            "id": num,
            "title": i.title,
        })
        num = num + 1

    return response


@router.post("/to_port")
async def get_history(num: int, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_active_user)):
    user_id = current_user.id
    stmt = select(Conversations).where(Conversations.user_id == user_id)
    result = await db.execute(stmt)
    conversations = result.scalars().all()
    port = conversations[num - 1].uuid

    return port


@router.post("/update_title")
async def get_history(num: int, title: str, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_active_user)):
    user_id = current_user.id
    stmt = select(Conversations).where(Conversations.user_id == user_id)
    result = await db.execute(stmt)
    conversations = result.scalars().all()
    id = conversations[num - 1].id
    stmt = update(Conversations).where(Conversations.id == id).values(title=title)
    await db.execute(stmt)
    await db.commit()
    return


@router.post("/delete")
async def get_history(num: int, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_active_user)):
    user_id = current_user.id
    stmt = select(Conversations).where(Conversations.user_id == user_id)
    result = await db.execute(stmt)
    conversations = result.scalars().all()
    uuid = conversations[num - 1].uuid

    stmt = delete(Messages).where(Messages.uuid == uuid)
    await db.execute(stmt)
    stmt = delete(Conversations).where(Conversations.uuid == uuid)
    await db.execute(stmt)

    await db.commit()

    return


@router.post("/port_id")
async def get_history(uuid: str, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_active_user)):
    user_id = current_user.id
    stmt = select(Conversations).where(Conversations.user_id == user_id)
    result = await db.execute(stmt)
    conversations = result.scalars().all()

    num = 1
    for i in conversations:
        if i.uuid == uuid:
            break
        else:
            num = num + 1

    return num


@router.post("/chat")
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    assistant = MultiAgentChatAssistant(request.model, request.func)
    if request.func == "novel":
        index = request.prompt.find("用户输入：")
        # 从"用户输入："的结束位置开始截取
        keep = request.prompt[(index + len("用户输入：")):]
        print(request.prompt)
        new_messages = Messages(
            uuid=request.uuid,  # 根据实际需求设置 UUID
            role='user',  # 必须是 'user', 'assistant', 'system' 中的值
            content=keep,
            model_name=request.model,
            time=request.time
        )
        db.add(new_messages)
        await db.commit()
        await db.refresh(new_messages)

    messages = request.messages.copy()

    # 记录 AI 响应到对话历史
    response = assistant.chat(request.prompt)

    if request.func == "novel":
        new_messages = Messages(
            uuid=request.uuid,
            role='assistant',
            content=response["output"],
            model_name=request.model,
            time=request.time
        )
        db.add(new_messages)
        await db.commit()
        await db.refresh(new_messages)
    else:
        result = await db.execute(
            select(Conversations).where(Conversations.uuid == request.uuid)
        )
        user = result.scalars().first()
        if request.func == "text2photo":
            user.photo_url = response
            await db.commit()
            await db.refresh(user)
            return response
        elif request.func == "relationship_diagram":
            user.peo_url = response["output"]
            await db.commit()
            await db.refresh(user)
    return response["output"]