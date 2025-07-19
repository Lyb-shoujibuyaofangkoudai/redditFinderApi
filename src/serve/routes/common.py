from fastapi import APIRouter, Depends, HTTPException, Query
from src.serve.models import DataResponse
from src.utils.logging import create_logger, info

# 配置日志
logger_config = create_logger("Reddit-API-Routes")
router = APIRouter()
@router.get("/test", response_model=DataResponse[str], summary="测试接口")
async def get_test(
        name: str = Query("test", description="test"),
):
    try:
        info(f"测试接口{name}", logger_config)
        return DataResponse(data=f"Hello {name}",  message="测试接口成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))