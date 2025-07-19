# src/main.py
import uvicorn
import os
import sys
from pathlib import Path


# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.serve.api import create_app
from src.config.env import get_settings, LANGSMITH_TRACING, LANGSMITH_ENDPOINT, LANGSMITH_API_KEY, \
    LANGSMITH_PROJECT  # 修改导入路径
from src.utils.logging import create_logger, info

# 配置日志
logger_config = create_logger("Reddit-Finder-API")

# 创建FastAPI应用
app = create_app()

# 获取配置
settings = get_settings()

def init_lang_smith():
    os.environ["LANGSMITH_TRACING"] = LANGSMITH_TRACING
    os.environ["LANGCHAIN_TRACING_V2"] = LANGSMITH_ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT

def main():
    """启动FastAPI服务"""
    info(f"启动 Reddit Finder API 服务 - 版本: {settings.app_version}", logger_config)
    info(f"环境: {settings.environment}", logger_config)
    info(f"API文档: http://{settings.host}:{settings.port}/docs", logger_config)
    
    # 启动服务
    uvicorn.run(
        "src.main:app",  # 修改为使用项目根目录的main.py
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
    init_lang_smith()

if __name__ == "__main__":
    main()