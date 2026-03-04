# app/domains/novels/schemas.py

from pydantic import BaseModel,  Field
from datetime import datetime
from typing import Optional


# 小说上传请求模型
class NovelCreate(BaseModel):
    title: str
    introduction: Optional[str] = None
    cover_url: Optional[str] = None  # 可选，允许不上传封面
    status: int = 0  # 默认草稿状态



# 小说信息响应模型，包含作者名、标题、创建日期、介绍、更新时间等
class NovelResponse(BaseModel):
    id: int
    author_name: str
    title: str
    introduction: str
    content: str
    tags: Optional[str] = None  # ✅ 添加字段
    cover_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

#接收请求体中的prompt和prompt_tags
class NovelUploadParams(BaseModel):
    prompt: str = Field(..., description="小说正文内容（必填）")
    prompt_tags: Optional[str] = Field(None, description="小说标签，用逗号分隔")


# 定义请求体模型（用于接收JSON参数）
class MapGenerateRequest(BaseModel):
    text: str
    conversation_uuid: str

class Config:
        orm_mode = True