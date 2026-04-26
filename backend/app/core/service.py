import os
import sys
from typing import List, Dict, Any

# 确保能加载到项目根目录的配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..", "..")
sys.path.append(PROJECT_ROOT)

from app.config import settings
from app.utils.logger import get_logger
from app.agent_logic import init_agent_service

logger = get_logger("StockService")

class StockAssistantService:
    """股票助手核心服务类"""
    
    def __init__(self):
        self.bot = None
        self._initialize_bot()

    def _initialize_bot(self):
        """初始化 Agent 实例"""
        try:
            logger.info(f"正在加载助手模块，使用模型: {settings.MODEL_NAME}")
            
            # 直接调用初始化函数
            self.bot = init_agent_service(
                model_name=settings.MODEL_NAME, 
                api_key=settings.API_KEY
            )
            
            # 显式打印已注册的工具列表（用于诊断）
            if hasattr(self.bot, 'function_map'):
                tool_names = list(self.bot.function_map.keys())
                logger.info(f"🔧 已注册工具列表: {tool_names}")
            else:
                logger.warning("⚠️ 无法获取 bot.function_map")
                
            logger.info("✅ 股票查询助手初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 助手初始化失败: {e}", exc_info=True)
            raise

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """处理对话请求"""
        if not self.bot:
            raise RuntimeError("助手未初始化")
        
        logger.info(f"🚀 开始处理对话，消息数: {len(messages)}")
        
        try:
            last_response = None
            for resp in self.bot.run(messages):
                last_response = resp
            
            if last_response and len(last_response) > 0:
                assistant_msg = last_response[-1]
                content = assistant_msg.get('content', '') if isinstance(assistant_msg, dict) else str(assistant_msg)
                logger.info("✅ 对话处理完成")
                return content
            else:
                return "抱歉，未能获取到回复。"
                
        except Exception as e:
            logger.error(f"❌ 对话处理异常: {e}", exc_info=True)
            raise

# 全局单例
assistant_service = StockAssistantService()
