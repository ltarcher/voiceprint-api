from fastapi import APIRouter
from ...models.voiceprint import HealthResponse
from ...core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/health",
    summary="健康检查",
    response_model=HealthResponse,
    description="检查服务运行状态",
)
async def health_check():
    """
    健康检查接口

    Returns:
        HealthResponse: 服务状态信息
    """
    return HealthResponse(
        status="healthy", message="3D-Speaker voiceprint API service running."
    )
