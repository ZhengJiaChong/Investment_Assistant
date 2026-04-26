from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import re

from app.core.agent import stock_agent
from app.utils.logger import get_logger

logger = get_logger("ChatAPI")
router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

async def generate_stream(request: ChatRequest):
    """生成流式响应数据"""
    messages = [{"role": msg.role, "content": msg.content} for msg in request.history]
    messages.append({"role": "user", "content": request.message})
    
    logger.info(f"开始流式处理，消息数: {len(messages)}")
    
    try:
        # 简化：直接输出所有 model stream 事件
        async for event in stock_agent.astream_events(
            {"messages": messages}, 
            version="v2"
        ):
            kind = event["event"]
            
            # 捕获模型输出流
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content and isinstance(content, str) and content.strip():
                    # 调试：打印包含 image_show 的内容
                    if 'image_show' in content:
                        logger.info(f"检测到图片URL: {content[:200]}")
                    yield f"data: {json.dumps({'type': 'content', 'data': content}, ensure_ascii=False)}\n\n"
        
        logger.info("流式输出完成")
        yield f"data: {json.dumps({'type': 'end'}, ensure_ascii=False)}\n\n"
    except Exception as e:
        logger.error(f"流式输出错误: {e}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'data': str(e)}, ensure_ascii=False)}\n\n"

@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """流式对话接口"""
    return StreamingResponse(
        generate_stream(request),
        media_type="text/event-stream"
    )
