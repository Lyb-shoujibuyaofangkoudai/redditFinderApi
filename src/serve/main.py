# src/serve/main.py
import uvicorn
import os
import sys
from pathlib import Path

from src.config.env import get_settings
from src.serve.api import create_app
from src.utils.logging import create_logger, info

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))



# 配置日志
logger_config = create_logger("Reddit-Finder-API")

# 创建FastAPI应用
app = create_app()

# 获取配置
settings = get_settings()

def main():
    """启动FastAPI服务"""
    info(f"启动 Reddit Finder API 服务 - 版本: {settings.app_version}", logger_config)
    info(f"环境: {settings.environment}", logger_config)
    info(f"API文档: http://{settings.host}:{settings.port}/docs", logger_config)
    
    # 启动服务
    uvicorn.run(
        "src.serve.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()