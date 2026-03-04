from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz
from contextlib import asynccontextmanager
from sqlalchemy.orm import configure_mappers
from app.db.session import AsyncSessionLocal, async_engine
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.novels import router as novels_router
from app.api.v1.endpoints.maps import router as maps_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.test import router as test_router
from app.api.v1.endpoints.fileload import router as fileload_router
from app.domains.users.models import User
from app.services.auth_service import get_user_by_username
from fastapi.staticfiles import StaticFiles

# 定义 lifespan 事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(User.metadata.create_all)
    await create_tables()
    yield  # 应用运行阶段
    # 关闭时无需操作，可留空

# 创建应用并绑定 lifespan
app = FastAPI(title="用户管理系统API", lifespan=lifespan)

# 配置 CORS
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 中间件：更新用户最后登录时间和在线状态
app.middleware("http")
async def update_user_activity(request: Request, call_next):
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            # 验证令牌并获取用户
            from jose import jwt
            from app.core.config import SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username:
                db = AsyncSessionLocal()
                try:
                    user = get_user_by_username(db, username)
                    if user:
                        # 更新最后登录时间
                        user.last_login_at = datetime.now(pytz.utc)
                        # 设置为在线状态
                        user.status = 1  # 1表示在线
                        await db.commit()
                finally:
                    await db.close()
        except:
            pass  # 忽略令牌验证错误
    response = await call_next(request)
    return response

# 挂载路由
app.include_router(auth_router, prefix="/api")
app.include_router(novels_router, prefix="/api")
app.include_router(maps_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(fileload_router, prefix="/api")
app.include_router(test_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
configure_mappers()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)