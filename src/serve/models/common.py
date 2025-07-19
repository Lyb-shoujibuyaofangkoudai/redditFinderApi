# src/serve/models/common.py
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field

T = TypeVar('T')

class ResponseBase(BaseModel):
    """API响应基类"""
    code: int = Field(1, description="响应代码 大于0为成功")
    success: bool = Field(True, description="请求是否成功")
    message: str = Field("操作成功", description="响应消息")

class DataResponse(ResponseBase, Generic[T]):
    """带数据的API响应"""
    data: T = Field(None, description="响应数据")

class PaginatedResponseBase(ResponseBase):
    """分页响应基类"""
    total: int = Field(0, description="总记录数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(10, description="每页记录数")
    total_pages: int = Field(0, description="总页数")

class PaginatedResponse(PaginatedResponseBase, Generic[T]):
    """分页数据响应"""
    items: List[T] = Field([], description="分页数据列表")

class ErrorResponse(ResponseBase):
    """错误响应"""
    code: int = Field(0, description="响应代码 0为失败")
    success: bool = Field(False, description="请求是否成功")
    error_code: str | int = Field(None, description="错误代码")
    detail: Optional[Any] = Field(None, description="错误详情")
    error_type: Optional[str] = Field(None, description="错误类型")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "success": False,
                "message": "操作失败",
                "error_code": "INTERNAL_ERROR",
                "detail": "服务器内部错误"
            }
        }