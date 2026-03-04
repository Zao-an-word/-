# core/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import DATABASE_URL
from ...domains.users.models import User


# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)  # echo=True用于调试，生产环境可关闭

# 会话工厂（用于创建数据库会话）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型类（所有ORM模型继承此类）
Base = declarative_base()

# 数据库会话依赖（供接口调用）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

User.metadata.create_all(bind=engine)