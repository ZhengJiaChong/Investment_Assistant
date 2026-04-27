import os
import sys
from typing import List, Dict, Any

# 确保能加载到项目根目录的配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..", "..")
sys.path.append(PROJECT_ROOT)

from app.config import settings
from app.utils.logger import get_logger
from app.core.agent import stock_agent

logger = get_logger("StockService")

class StockAssistantService:
    """股票助手核心服务类（已废弃，使用 LangChain Agent）"""
    
    def __init__(self):
        # 注意：此服务类已废弃，直接使用 app.core.agent.stock_agent
        logger.warning("StockAssistantService 已废弃，请使用 LangChain Agent")

# 全局单例
assistant_service = StockAssistantService()
