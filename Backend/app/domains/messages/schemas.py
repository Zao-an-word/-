from pydantic import BaseModel, Field, ConfigDict, constr
from datetime import datetime
from enum import Enum
from typing import Optional


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(BaseModel):
    conversation_id: int = Field(..., gt=0, description="所属会话ID")
    role: MessageRole = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    message_id: Optional[str] = Field(default=None, max_length=64, description="模型返回的消息ID")
    tokens: int = Field(default=0, ge=0, description="消息token数")
    model_name: str = Field(..., max_length=45, description="使用的模型名称")


class MessageCreate(MessageBase):
    pass


class MessageUpdate(MessageBase):
    conversation_id: Optional[int] = Field(default=None, gt=0, description="所属会话ID")
    role: Optional[MessageRole] = Field(default=None, description="消息角色")
    content: Optional[str] = Field(default=None, description="消息内容")


class MessageResponse(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime