from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import List
from ...models.voiceprint import VoiceprintRegisterResponse, VoiceprintIdentifyResponse
from ...services.voiceprint_service import voiceprint_service
from ...api.dependencies import AuthorizationToken
from ...core.logging import get_logger

# 创建安全模式
security = HTTPBearer(description="接口令牌")

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/register",
    summary="声纹注册",
    response_model=VoiceprintRegisterResponse,
    description="注册新的声纹特征",
    dependencies=[Depends(security)],
)
async def register_voiceprint(
    token: AuthorizationToken,
    speaker_id: str = Form(..., description="说话人ID"),
    file: UploadFile = File(..., description="WAV音频文件"),
):
    """
    注册声纹接口

    Args:
        token: 接口令牌（Header）
        speaker_id: 说话人ID
        file: 说话人音频文件（WAV）

    Returns:
        VoiceprintRegisterResponse: 注册结果
    """
    try:
        # 验证文件类型
        if not file.filename.lower().endswith(".wav"):
            raise HTTPException(status_code=400, detail="只支持WAV格式音频文件")

        # 读取音频数据
        audio_bytes = await file.read()

        # 注册声纹
        success = voiceprint_service.register_voiceprint(speaker_id, audio_bytes)

        if success:
            return VoiceprintRegisterResponse(success=True, msg=f"已登记: {speaker_id}")
        else:
            raise HTTPException(status_code=500, detail="声纹注册失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"声纹注册异常: {e}")
        raise HTTPException(status_code=500, detail=f"声纹注册失败: {str(e)}")


@router.post(
    "/identify",
    summary="声纹识别",
    response_model=VoiceprintIdentifyResponse,
    description="识别音频中的说话人",
    dependencies=[Depends(security)],
)
async def identify_voiceprint(
    token: AuthorizationToken,
    speaker_ids: str = Form(..., description="候选说话人ID，逗号分隔"),
    file: UploadFile = File(..., description="WAV音频文件"),
):
    """
    声纹识别接口

    Args:
        token: 接口令牌（Header）
        speaker_ids: 候选说话人ID，逗号分隔
        file: 待识别音频文件（WAV）

    Returns:
        VoiceprintIdentifyResponse: 识别结果
    """
    try:
        # 验证文件类型
        if not file.filename.lower().endswith(".wav"):
            raise HTTPException(status_code=400, detail="只支持WAV格式音频文件")

        # 解析候选说话人ID
        candidate_ids = [x.strip() for x in speaker_ids.split(",") if x.strip()]
        if not candidate_ids:
            raise HTTPException(status_code=400, detail="候选说话人ID不能为空")

        # 读取音频数据
        audio_bytes = await file.read()

        # 识别声纹
        match_name, match_score = voiceprint_service.identify_voiceprint(
            candidate_ids, audio_bytes
        )

        return VoiceprintIdentifyResponse(speaker_id=match_name, score=match_score)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"声纹识别异常: {e}")
        raise HTTPException(status_code=500, detail=f"声纹识别失败: {str(e)}")


@router.delete(
    "/{speaker_id}",
    summary="删除声纹",
    description="删除指定说话人的声纹特征",
    dependencies=[Depends(security)],
)
async def delete_voiceprint(
    token: AuthorizationToken,
    speaker_id: str,
):
    """
    删除声纹接口

    Args:
        token: 接口令牌（Header）
        speaker_id: 说话人ID

    Returns:
        dict: 删除结果
    """
    try:
        success = voiceprint_service.delete_voiceprint(speaker_id)

        if success:
            return {"success": True, "msg": f"已删除: {speaker_id}"}
        else:
            raise HTTPException(status_code=404, detail=f"未找到说话人: {speaker_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除声纹异常 {speaker_id}: {e}")
        raise HTTPException(status_code=500, detail=f"删除声纹失败: {str(e)}")


@router.get(
    "/stats",
    summary="获取统计信息",
    description="获取声纹数据库统计信息",
    dependencies=[Depends(security)],
)
async def get_stats(
    token: AuthorizationToken,
):
    """
    获取统计信息接口

    Args:
        token: 接口令牌（Header）

    Returns:
        dict: 统计信息
    """
    try:
        count = voiceprint_service.get_voiceprint_count()
        return {"total_voiceprints": count, "status": "healthy"}
    except Exception as e:
        logger.error(f"获取统计信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
