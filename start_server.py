#!/usr/bin/env python3
"""
生产环境启动脚本
"""

import os
import sys
import socket
import signal
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.logging import setup_logging, get_logger

# 设置日志
setup_logging()
logger = get_logger(__name__)


def get_local_ip():
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"收到信号 {signum}，正在优雅关闭服务...")
    sys.exit(0)


def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        logger.info(
            f"生产环境服务启动中（Uvicorn），监听地址: {settings.host}:{settings.port}"
        )
        print("=" * 60)
        local_ip = get_local_ip()
        print(
            f"声纹接口地址: http://{local_ip}:{settings.port}/voiceprint/health?key="
            + settings.api_token
        )
        print("=" * 60)

        # 使用Uvicorn启动，配置优化
        uvicorn.run(
            "app.application:app",
            host=settings.host,
            port=settings.port,
            reload=False,  # 生产环境关闭热重载
            workers=1,  # 单进程模式，避免模型重复加载
            access_log=True,  # 开启访问日志
            log_level="info",
            timeout_keep_alive=30,  # keep-alive超时
            timeout_graceful_shutdown=300,  # 优雅关闭超时
            limit_concurrency=1000,  # 并发连接限制
            limit_max_requests=1000,  # 最大请求数限制
            backlog=2048,  # 连接队列大小
        )

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在退出服务。")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise


if __name__ == "__main__":
    main()
