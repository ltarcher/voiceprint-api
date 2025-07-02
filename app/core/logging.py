import logging
import sys
from typing import Optional
from .config import settings


def setup_logging(
    level: Optional[str] = None, format_string: Optional[str] = None
) -> None:
    """
    设置应用日志配置

    Args:
        level: 日志级别
        format_string: 日志格式
    """
    # 获取配置
    log_level = level or settings.logging.get("level", "INFO")
    log_format = format_string or settings.logging.get(
        "format", "%(asctime)s %(levelname)s %(message)s"
    )

    # 设置日志级别
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # 配置根日志记录器
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("voiceprint_api.log", encoding="utf-8"),
        ],
    )

    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info(f"日志系统初始化完成，级别: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)
