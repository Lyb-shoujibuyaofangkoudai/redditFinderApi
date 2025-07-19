# src/serve/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from src.config.env import get_settings  # 修改导入路径
from src.serve.exceptions import setup_exception_handlers
from src.serve.routes import router as api_router
from src.serve.middleware.logging import LoggingMiddleware
from src.utils.logging import create_logger, info, error

# 配置日志
logger_config = create_logger("Reddit-API")

def create_app() -> FastAPI:
    """创建并配置FastAPI应用程序
    
    Returns:
        FastAPI: 配置好的FastAPI应用程序实例
    """
    settings = get_settings()
    
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加日志中间件
    app.add_middleware(LoggingMiddleware)
    setup_exception_handlers(app)
    # 注册路由
    app.include_router(api_router, prefix=settings.api_prefix)
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup 事件
        info("API服务启动", logger_config)

        yield  # 应用运行期间

        # Shutdown 事件
        info("API服务关闭", logger_config)
    return app