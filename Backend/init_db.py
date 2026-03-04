# init_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL
# 引入你的模型定义
from app.domains.users.models import User
from app.domains.novels.models import Novels
from app.domains.conversations.models import Conversations
from app.domains.messages.models import Messages

# 引入 Base
from app.db.base import Base

# 初始化 SQLAlchemy 引擎
engine = create_engine(DATABASE_URL, echo=True)

# 创建所有表（保留外键顺序）
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ 所有表已创建成功")

if __name__ == "__main__":
    init_db()
