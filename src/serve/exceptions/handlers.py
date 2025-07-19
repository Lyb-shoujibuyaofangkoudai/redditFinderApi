# src/serve/exceptions/handlers.py
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.serve.models.common import ErrorResponse
from src.utils.logging import create_logger, error

# 配置日志
logger_config = create_logger("API-Exception-Handlers")

def setup_exception_handlers(app: FastAPI) -> None:
    """设置FastAPI应用的异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """处理HTTP异常"""
        error(f"HTTP异常: {exc.detail}", logger_config)
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code=exc.status_code,
                error_code=exc.status_code,
                message=f"HTTP异常：{str(exc.detail)}",
                error_type="http_exception",
                success=False
            ).model_dump()
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """处理请求验证异常"""
        error(f"请求异常：{request.url}，{request.method}，{exc.body}")
        error_details = []
        for err in exc.errors():
            error_details.append({
                "loc": err["loc"],
                "msg": err["msg"],
                "type": err["type"]
            })
        
        error(f"请求验证异常: {error_details}", logger_config)
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                code=422,
                error_code=422,
                message=f"请求参数验证失败：{error_details[0]['msg']}",
                error_type="validation_error",
                detail=error_details,
                success=False
            ).model_dump()
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """处理Pydantic验证异常"""
        error_details = []
        for err in exc.errors():
            error_details.append({
                "loc": err["loc"],
                "msg": err["msg"],
                "type": err["type"]
            })
        
        error(f"Pydantic验证异常: {error_details}", logger_config)
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                code=422,
                message=f"数据验证失败：{error_details[0]['msg']}",
                error_type="pydantic_validation_error",
                detail=error_details,
                success=False,
                error_code=422
            ).model_dump()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """处理一般异常"""
        error(f"一般异常: {str(exc)}", logger_config)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code=0,
                message=str(exc),
                error_type="error",
                detail=str(exc),
                success=False,
                error_code=0
            ).model_dump()
        )