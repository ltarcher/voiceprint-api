from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .api.v1.api import api_router


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""

    # 创建安全模式
    security = HTTPBearer(description="接口令牌")

    # 创建应用
    app = FastAPI(
        title="3D-Speaker 声纹识别API",
        description="基于3D-Speaker的声纹注册与识别服务",
        version="2.0.0",
        docs_url="/voiceprint/docs",
        redoc_url="/voiceprint/redoc",
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境中应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册API路由
    app.include_router(api_router, prefix="/voiceprint")

    # 根路径
    @app.get("/", include_in_schema=False)
    def root():
        """根路径，自动跳转到API文档"""
        return RedirectResponse(url="/voiceprint/docs")

    # /voiceprint/ 跳转到 /voiceprint/docs
    @app.get("/voiceprint/", include_in_schema=False)
    def voiceprint_root():
        return RedirectResponse(url="/voiceprint/docs")

    return app


# 创建应用实例
app = create_app()
