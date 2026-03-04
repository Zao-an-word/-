from sqlalchemy import TEXT, Enum, create_engine, Column, Integer, String, DateTime, Boolean, func

from ...db.base import Base

class Messages(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(60))
    role = Column(Enum('user', 'assistant', 'system'))
    content = Column(TEXT)
    created_at = Column(DateTime, default=func.now())
    model_name = Column(String(45))
    time = Column(String(45))