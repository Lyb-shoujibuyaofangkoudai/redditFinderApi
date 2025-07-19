# src/serve/routes/__init__.py
from fastapi import APIRouter

from src.serve.routes.reddit import router as reddit_router
from src.serve.routes.common import router as common_router

# 创建主路由
router = APIRouter()

# 注册子路由
router.include_router(reddit_router, prefix="/reddit", tags=["Reddit"])
router.include_router(common_router,  prefix="/common", tags=["Common"])
