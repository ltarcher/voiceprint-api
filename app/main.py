import socket
import uvicorn

from .core.config import settings
from .core.logging import setup_logging, get_logger
from .application import app

# 设置日志
setup_logging()
logger = get_logger(__name__)


def get_local_ip() -> str:
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    try:
        logger.info(
            f"开发环境服务启动中，监听地址: {settings.host}:{settings.port}，"
            f"文档: http://{settings.host}:{settings.port}/voiceprint/docs"
        )
        print("=" * 60)
        local_ip = get_local_ip()
        print(
            f"声纹接口地址: http://{local_ip}:{settings.port}/voiceprint/health?key="
            + settings.api_token
        )
        print("=" * 60)

        # 启动服务
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=True,  # 开发环境开启热重载
            workers=1,  # 单进程模式，避免模型重复加载
        )
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在退出服务。")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise
