#大语言模型服务
from ..domains.users.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from ..domains.conversations.models import Conversations
import uuid
from fastapi import Depends
from .auth_service import get_current_active_user

async def assign_port(
        db: AsyncSession,
        current_user: User
) -> str:
        # 检查会话是否已有端口
        unique_id = uuid.uuid4().hex
        new_conversation = Conversations(
            user_id = current_user.id,
            uuid = unique_id,
            title='新对话'

        )
        db.add(new_conversation)
        await db.commit()
        await db.refresh(new_conversation)
        return unique_id