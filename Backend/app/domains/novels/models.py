from datetime import datetime
from sqlalchemy import  Column, DateTime, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..users.models import User
from ...db.base import Base

class NovelStatus:
    DRAFT = 1      # 草稿
    PUBLISHED = 2  # 已发布
    ARCHIVED = 3   # 已归档
# 小说模型
class Novels(Base):
    __tablename__ = "novels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String(100), nullable=False)
    introduction = Column(Text)
    content = Column(Text, nullable=False)
    cover_url = Column(String(255))
    status = Column(Integer, default=0)
    tags = Column(String(45))

    created_at = Column(DateTime, default=datetime)
    updated_at = Column(DateTime, default=datetime)

    author = relationship(User)

    conversations = relationship("Conversations", back_populates="novel")