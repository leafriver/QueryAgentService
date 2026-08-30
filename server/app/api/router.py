"""API 路由汇总，后续新增的模块路由统一在此注册。"""

from fastapi import APIRouter

from app.api.endpoints import auth, chat, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/conversations", tags=["chat"])
