# app/domains/conversations/schemas.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from ....app.domains.users.schemas import UserResponse
from typing import Optional, List

class MessageBase(BaseModel):
    role: str
    content: str



class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class ConversationBase(BaseModel):
    title: str


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []
    user: UserResponse | None = None