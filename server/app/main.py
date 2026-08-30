"""QueryAgentService 后端服务入口。

启动方式：
    cd server
    uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  确保 ORM 模型注册到 Base.metadata
from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时自动建表（开发阶段使用，后续可引入 Alembic 做迁移管理）
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# 开发环境下允许前端跨域访问
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root() -> dict:
    """健康检查接口。"""
    return {
        "project": settings.PROJECT_NAME,
        "docs": "/docs",
        "api_prefix": settings.API_V1_STR,
    }
