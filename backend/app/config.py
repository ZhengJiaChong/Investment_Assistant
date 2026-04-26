import os
from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
load_dotenv()

class Settings:
    """项目配置中心"""
    
    # --- 基础配置 ---
    PROJECT_NAME = "ChatBI Stock Assistant"
    VERSION = "1.0.0"
    DEBUG = True
    
    # --- 路径配置 ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.join(BASE_DIR, "..")  # backend/app -> backend
    WORKSPACE_ROOT = os.path.join(PROJECT_ROOT, "..") # backend -> 根目录
    
    DB_PATH = r"J:\agent\case-投资助手\gold_data.db"
    FAQ_PATH = os.path.join(WORKSPACE_ROOT, "faq.txt")
    IMAGE_DIR = os.path.join(WORKSPACE_ROOT, "image_show")
    
    # --- 模型配置 (OpenRouter) ---
    MODEL_NAME = os.getenv("MODEL_NAME", "tencent/hy3-preview:free")
    MODEL_SERVER = os.getenv("MODEL_SERVER", "https://openrouter.ai/api/v1")
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # --- 助手配置 ---
    TEMPERATURE = 0.7
    MCP_TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")

settings = Settings()
