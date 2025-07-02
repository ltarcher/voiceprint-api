#!/usr/bin/env python3
"""
生产环境启动脚本
支持高并发部署
"""

import os
import sys
import socket
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


def main():
    """主函数"""
    try:
        logger.info(f"生产环境服务启动中，监听地址: {settings.host}:{settings.port}")
        print("=" * 60)
        local_ip = get_local_ip()
        print(
            f"声纹接口地址: http://{local_ip}:{settings.port}/voiceprint/health?key="
            + settings.api_token
        )
        print("=" * 60)

        # 使用gunicorn启动，支持高并发
        import gunicorn.app.base

        class StandaloneApplication(gunicorn.app.base.BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                config = {
                    key: value
                    for key, value in self.options.items()
                    if key in self.cfg.settings and value is not None
                }
                for key, value in config.items():
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        options = {
            "bind": f"{settings.host}:{settings.port}",
            "workers": 1,  # 单进程模式，避免模型重复加载
            "worker_class": "uvicorn.workers.UvicornWorker",  # 使用UvicornWorker支持ASGI
            "worker_connections": 1000,  # 每个worker的连接数
            "max_requests": 1000,  # 每个worker处理的最大请求数
            "max_requests_jitter": 100,  # 随机抖动，避免同时重启
            "timeout": 120,  # 请求超时时间
            "keepalive": 2,  # keep-alive连接数
            "preload_app": True,  # 预加载应用
            "access_log_format": '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s',
            "accesslog": "-",  # 访问日志输出到stdout
            "errorlog": "-",  # 错误日志输出到stderr
            "loglevel": "info",
        }

        from app.application import app

        StandaloneApplication(app, options).run()

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在退出服务。")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise


if __name__ == "__main__":
    main()
