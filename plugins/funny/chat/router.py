from fastapi import APIRouter

from common.biz import result
from plugins.funny.chat.utils import chat_ai

chat = APIRouter()


@chat.post("/chat")
async def send_message(
  prompt: str,
  user_id: int = 0,
  ai: bool = False,
):
  ...
  # if ai:
  #   msg = chat_ai(prompt,{})
  #   if not msg:
  #     return result.fail({"message": "AI连接失败"})
  #   return result.success({"message": msg.strip()})
  # msg = await fetch_chat_response(prompt)
  # if msg:
  #   msg = await process_message(msg)
  #   return result.success({"message": msg.strip()})
  # else:
  #   return result.fail({"message": "没有获取到有效的消息"})
