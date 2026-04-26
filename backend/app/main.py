"""
FastAPI 企业级后端入口
"""
import sys
import os

# 确保能加载到项目根目录的配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..")
sys.path.append(PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.api.chat import router as chat_router
from app.utils.logger import get_logger

logger = get_logger("Main")

# 初始化 FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="股票投资助手 API 服务"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录 (用于访问生成的股票图表)
image_dir = os.path.join(settings.WORKSPACE_ROOT, "image_show")
if os.path.exists(image_dir):
    app.mount("/image_show", StaticFiles(directory=image_dir), name="images")

# 注册业务路由
app.include_router(chat_router, prefix="/api", tags=["Chat"])

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy", 
        "model": settings.MODEL_NAME,
        "version": settings.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"正在启动 {settings.PROJECT_NAME} v{settings.VERSION}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
