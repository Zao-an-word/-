from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import DATABASE_URL  # 注意：DATABASE_URL 需使用异步驱动格式

# 创建异步数据库引擎（需使用异步驱动的 URL，如 postgresql+asyncpg:// 或 mysql+aiomysql://）
async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False  # 生产环境建议关闭，调试时可打开查看 SQL 日志
)

# 创建异步会话工厂（替代同步的 sessionmaker）
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,  # 指定为异步会话类
    autocommit=False,
    autoflush=False,
    expire_on_commit=False  # 异步模式下建议关闭，避免自动过期
)

# 基类（与同步版本一致，无需修改）
Base = declarative_base()

# 异步获取数据库会话的依赖项（替代同步的 get_db）
async def get_db():
    async with AsyncSessionLocal() as db:  # 异步上下文管理器
        try:
            yield db
        finally:
            await db.close()  # 异步关闭会话