import os
import tempfile
import soundfile as sf
import librosa
import numpy as np
from typing import Tuple
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class AudioProcessor:
    """音频处理工具类"""

    def __init__(self):
        self.target_sample_rate = settings.target_sample_rate
        self.tmp_dir = settings.tmp_dir
        # 确保临时目录存在
        os.makedirs(self.tmp_dir, exist_ok=True)

    def ensure_16k_wav(self, audio_bytes: bytes) -> str:
        """
        将任意采样率的wav bytes转为16kHz wav临时文件

        Args:
            audio_bytes: 音频字节数据

        Returns:
            str: 临时文件路径
        """
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".wav", dir=self.tmp_dir
        ) as tmpf:
            tmpf.write(audio_bytes)
            tmp_path = tmpf.name

        try:
            # 读取原采样率
            data, sr = sf.read(tmp_path)

            if sr != self.target_sample_rate:
                # librosa重采样，支持多通道
                if data.ndim == 1:
                    data_rs = librosa.resample(
                        data, orig_sr=sr, target_sr=self.target_sample_rate
                    )
                else:
                    data_rs = np.vstack(
                        [
                            librosa.resample(
                                data[:, ch],
                                orig_sr=sr,
                                target_sr=self.target_sample_rate,
                            )
                            for ch in range(data.shape[1])
                        ]
                    ).T

                # 写入重采样后的音频
                sf.write(tmp_path, data_rs, self.target_sample_rate)
                logger.debug(f"音频重采样: {sr}Hz -> {self.target_sample_rate}Hz")

            return tmp_path

        except Exception as e:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            logger.error(f"音频处理失败: {e}")
            raise

    def validate_audio_file(self, audio_bytes: bytes) -> bool:
        """
        验证音频文件格式是否有效

        Args:
            audio_bytes: 音频字节数据

        Returns:
            bool: 音频文件是否有效
        """
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".wav", dir=self.tmp_dir
            ) as tmpf:
                tmpf.write(audio_bytes)
                tmp_path = tmpf.name

            # 尝试读取音频文件
            data, sr = sf.read(tmp_path)

            # 检查音频数据
            if len(data) == 0:
                logger.warning("音频文件为空")
                return False

            # 检查采样率
            if sr < 8000:  # 最低采样率要求
                logger.warning(f"采样率过低: {sr}Hz")
                return False

            # 检查音频时长（至少0.5秒，最多30秒）
            duration = len(data) / sr
            if duration < 0.5:
                logger.warning(f"音频时长过短: {duration:.2f}秒")
                return False
            elif duration > 30:
                logger.warning(f"音频时长过长: {duration:.2f}秒")
                return False

            logger.debug(f"音频验证通过: {duration:.2f}秒, {sr}Hz")
            return True

        except Exception as e:
            logger.error(f"音频文件验证失败: {e}")
            return False
        finally:
            # 清理临时文件
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

    def cleanup_temp_file(self, file_path: str) -> None:
        """
        清理临时文件

        Args:
            file_path: 临时文件路径
        """
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"临时文件已清理: {file_path}")
        except Exception as e:
            logger.warning(f"清理临时文件失败 {file_path}: {e}")


# 全局音频处理器实例
audio_processor = AudioProcessor()
