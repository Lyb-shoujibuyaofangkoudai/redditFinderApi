# src/config/env.py
import os
from typing import List
from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# 加载项目根目录的.env文件
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Reddit API配置
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "")
DEVELOPER = os.getenv("DEVELOPER", "")
PASSWORD = os.getenv("PASSWORD", "")
REDDIT_API_TIMEOUT = float(os.getenv("REDDIT_API_TIMEOUT", "0.5"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "1000"))

# 监控配置
SUBREDDITS = os.getenv("SUBREDDITS", "all")
KEYWORDS = os.getenv("KEYWORDS", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "")

# OpenAI API配置
API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "")
MODEL = os.getenv("MODEL", "")

#  日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

# langsmith
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "reddit-finder")




class Settings(BaseSettings):
    """API服务配置类
    
    使用Pydantic的BaseSettings来管理配置，支持从环境变量加载配置
    """
    # 应用信息
    app_name: str = os.getenv("API_APP_NAME", "Reddit Finder API")
    app_description: str = os.getenv("API_APP_DESCRIPTION", "Reddit内容发现和分析的API服务")
    app_version: str = os.getenv("API_APP_VERSION", "0.1.0")
    
    # API配置
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    docs_url: str = os.getenv("API_DOCS_URL", "/docs")
    redoc_url: str = os.getenv("API_REDOC_URL", "/redoc")
    
    # 服务器配置
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("API_DEBUG", "True").lower() in ("true", "1", "t")
    reload: bool = os.getenv("API_RELOAD", "True").lower() in ("true", "1", "t")
    environment: str = os.getenv("API_ENVIRONMENT", "development")
    
    # CORS配置
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    
    # 缓存配置
    cache_expiration: int = int(os.getenv("API_CACHE_EXPIRATION", "300"))  # 缓存过期时间（秒）
    
    # 限流配置
    rate_limit_requests: int = int(os.getenv("API_RATE_LIMIT_REQUESTS", "100"))  # 每分钟最大请求数
    
    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置，使用lru_cache缓存结果

    Returns:
        Settings: 配置实例
    """
    return Settings()
