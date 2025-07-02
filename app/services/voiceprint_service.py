import numpy as np
import torch
from typing import Dict, List, Tuple, Optional
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from ..core.config import settings
from ..core.logging import get_logger
from ..database.voiceprint_db import voiceprint_db
from ..utils.audio_utils import audio_processor

logger = get_logger(__name__)


class VoiceprintService:
    """声纹识别服务类"""

    def __init__(self):
        self._pipeline = None
        self.similarity_threshold = settings.similarity_threshold
        self._init_pipeline()

    def _init_pipeline(self) -> None:
        """初始化声纹识别模型"""
        try:
            self._pipeline = pipeline(
                task=Tasks.speaker_verification,
                model="iic/speech_campplus_sv_zh-cn_3dspeaker_16k",
            )
            logger.info("声纹模型加载成功")
        except Exception as e:
            logger.error(f"声纹模型加载失败: {e}")
            raise

    def _to_numpy(self, x) -> np.ndarray:
        """
        将torch tensor或其他类型转为numpy数组

        Args:
            x: 输入数据

        Returns:
            np.ndarray: numpy数组
        """
        return x.cpu().numpy() if torch.is_tensor(x) else np.asarray(x)

    def extract_voiceprint(self, audio_path: str) -> np.ndarray:
        """
        从音频文件中提取声纹特征

        Args:
            audio_path: 音频文件路径

        Returns:
            np.ndarray: 声纹特征向量
        """
        try:
            result = self._pipeline([audio_path], output_emb=True)
            emb = self._to_numpy(result["embs"][0]).astype(np.float32)
            logger.debug(f"声纹特征提取成功，维度: {emb.shape}")
            return emb
        except Exception as e:
            logger.error(f"声纹特征提取失败: {e}")
            raise

    def calculate_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        计算两个声纹特征的相似度

        Args:
            emb1: 声纹特征1
            emb2: 声纹特征2

        Returns:
            float: 相似度分数 (0-1)
        """
        try:
            # 使用余弦相似度
            similarity = np.dot(emb1, emb2) / (
                np.linalg.norm(emb1) * np.linalg.norm(emb2)
            )
            return float(similarity)
        except Exception as e:
            logger.error(f"相似度计算失败: {e}")
            return 0.0

    def register_voiceprint(self, speaker_id: str, audio_bytes: bytes) -> bool:
        """
        注册声纹

        Args:
            speaker_id: 说话人ID
            audio_bytes: 音频字节数据

        Returns:
            bool: 注册是否成功
        """
        audio_path = None
        try:
            # 验证音频文件
            if not audio_processor.validate_audio_file(audio_bytes):
                logger.warning(f"音频文件验证失败: {speaker_id}")
                return False

            # 处理音频文件
            audio_path = audio_processor.ensure_16k_wav(audio_bytes)

            # 提取声纹特征
            emb = self.extract_voiceprint(audio_path)

            # 保存到数据库
            success = voiceprint_db.save_voiceprint(speaker_id, emb)

            if success:
                logger.info(f"声纹注册成功: {speaker_id}")
            else:
                logger.error(f"声纹注册失败: {speaker_id}")

            return success

        except Exception as e:
            logger.error(f"声纹注册异常 {speaker_id}: {e}")
            return False
        finally:
            # 清理临时文件
            if audio_path:
                audio_processor.cleanup_temp_file(audio_path)

    def identify_voiceprint(
        self, speaker_ids: List[str], audio_bytes: bytes
    ) -> Tuple[str, float]:
        """
        识别声纹

        Args:
            speaker_ids: 候选说话人ID列表
            audio_bytes: 音频字节数据

        Returns:
            Tuple[str, float]: (识别出的说话人ID, 相似度分数)
        """
        audio_path = None
        try:
            # 验证音频文件
            if not audio_processor.validate_audio_file(audio_bytes):
                logger.warning("音频文件验证失败")
                return "", 0.0

            # 处理音频文件
            audio_path = audio_processor.ensure_16k_wav(audio_bytes)

            # 提取声纹特征
            test_emb = self.extract_voiceprint(audio_path)

            # 获取候选声纹特征
            voiceprints = voiceprint_db.get_voiceprints(speaker_ids)
            if not voiceprints:
                logger.info("未找到候选说话人声纹")
                return "", 0.0

            # 计算相似度
            similarities = {}
            for name, emb in voiceprints.items():
                similarity = self.calculate_similarity(test_emb, emb)
                similarities[name] = similarity

            # 找到最佳匹配
            if not similarities:
                return "", 0.0

            match_name = max(similarities, key=similarities.get)
            match_score = similarities[match_name]

            # 检查是否超过阈值
            if match_score < self.similarity_threshold:
                logger.info(f"未识别到说话人，最高分: {match_score:.4f}")
                return "", match_score

            logger.info(f"识别到说话人: {match_name}, 分数: {match_score:.4f}")
            return match_name, match_score

        except Exception as e:
            logger.error(f"声纹识别异常: {e}")
            return "", 0.0
        finally:
            # 清理临时文件
            if audio_path:
                audio_processor.cleanup_temp_file(audio_path)

    def delete_voiceprint(self, speaker_id: str) -> bool:
        """
        删除声纹

        Args:
            speaker_id: 说话人ID

        Returns:
            bool: 删除是否成功
        """
        return voiceprint_db.delete_voiceprint(speaker_id)

    def get_voiceprint_count(self) -> int:
        """
        获取声纹总数

        Returns:
            int: 声纹总数
        """
        return voiceprint_db.count_voiceprints()


# 全局声纹服务实例
voiceprint_service = VoiceprintService()
