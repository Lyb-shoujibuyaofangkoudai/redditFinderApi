# src/serve/dependencies/services.py
from fastapi import Depends

from src.serve.services.reddit_service import RedditService, get_reddit_service

def get_reddit_service_dependency() -> RedditService:
    """获取Reddit服务依赖
    
    用于FastAPI的依赖注入系统
    
    Returns:
        RedditService: Reddit服务实例
    """
    return get_reddit_service()