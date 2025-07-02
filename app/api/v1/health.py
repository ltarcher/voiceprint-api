from fastapi import APIRouter, HTTPException, Query
from ...services.voiceprint_service import voiceprint_service
from ...core.logging import get_logger
from ...core.config import settings

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/health",
    summary="健康检查",
    response_model=dict,
    description="检查服务运行状态，需要提供正确的密钥",
)
async def health_check(
    key: str = Query(..., description="访问密钥", example="your-secret-key")
):
    """
    健康检查接口

    Args:
        key: 访问密钥，必须与配置中的authorization密钥匹配

    Returns:
        dict: 服务状态信息

    Raises:
        HTTPException: 当密钥不正确时返回401错误
    """
    # 验证密钥
    if key != settings.api_token:
        logger.warning(f"健康检查接口收到无效密钥: {key}")
        raise HTTPException(status_code=401, detail="密钥验证失败")

    try:
        count = voiceprint_service.get_voiceprint_count()
        return {"total_voiceprints": count, "status": "healthy"}
    except Exception as e:
        logger.error(f"获取统计信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
