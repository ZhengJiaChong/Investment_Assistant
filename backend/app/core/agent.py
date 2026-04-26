import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from app.core.tools import get_stock_tools
from app.utils.logger import get_logger

logger = get_logger("LangChainAgent")

def create_stock_agent():
    """Create a LangGraph ReAct Agent for stock analysis."""
    
    # 1. 初始化 LLM (使用 OpenRouter)
    llm = ChatOpenAI(
        model="tencent/hy3-preview:free",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.7
    )
    
    # 2. 获取工具
    tools = get_stock_tools()
    
    # 3. 创建 Agent (基于 LangGraph)
    agent = create_react_agent(llm, tools)
    
    logger.info(f"✅ LangChain Agent created with {len(tools)} tools.")
    return agent

stock_agent = create_stock_agent()
