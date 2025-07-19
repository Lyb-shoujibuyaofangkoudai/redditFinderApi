# src/serve/middleware/logging.py
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.utils.logging import create_logger, info, error

# 配置日志
logger_config = create_logger("Reddit-API-Middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件
    
    记录API请求和响应的详细信息
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录日志
        
        Args:
            request: 请求对象
            call_next: 下一个处理函数
            
        Returns:
            Response: 响应对象
        """
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        request_id = request.headers.get("X-Request-ID", "")
        client_ip = request.client.host if request.client else "unknown"
        
        info(
            f"请求开始 | ID: {request_id} | 方法: {request.method} | 路径: {request.url.path} | "
            f"客户端: {client_ip} | 查询参数: {request.query_params}",
            logger_config
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            info(
                f"请求完成 | ID: {request_id} | 状态码: {response.status_code} | "
                f"处理时间: {process_time:.4f}秒",
                logger_config
            )
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 记录异常信息
            process_time = time.time() - start_time
            error(
                f"请求异常 | ID: {request_id} | 路径: {request.url.path} | "
                f"处理时间: {process_time:.4f}秒 | 异常: {str(e)}",
                logger_config
            )
            raise