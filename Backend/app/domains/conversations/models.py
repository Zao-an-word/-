# app/domains/conversations/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Text
from sqlalchemy.orm import relationship
from ...db.base import Base
from sqlalchemy import DateTime, func

#对话模型
class Conversations(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer,ForeignKey("user.id"), nullable=False)
    title = Column(String(128))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, onupdate=func.now(), server_default=func.now())
    status = Column(Integer)
    uuid = Column(String(60))
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    map_url = Column(String(128))
    peo_url = Column(Text)
    photo_url = Column(String(400))

    user = relationship("User", back_populates="conversations")
    novel = relationship("Novels", back_populates="conversations")