#路由汇总
# app/api/v1/router.py
from fastapi import APIRouter
from .endpoints import auth  # 导入认证路由
from .endpoints import novels
from .endpoints import maps
from .endpoints import fileload
# 创建聚合路由实例
api_router = APIRouter()

# 注册认证相关路由（所有/auth接口会被挂载到/api/v1/auth）
api_router.include_router(auth.router)
api_router.include_router(novels.router)
api_router.include_router(maps.router)
api_router.include_router(fileload.router)
# 未来可添加其他路由（如chat、conversations等）
# from app.api.v1.endpoints import chat
# api_router.include_router(chat.router, prefix="/chat")
