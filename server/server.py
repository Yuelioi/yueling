import json
from typing import cast

from fastapi import FastAPI, File, Form, UploadFile
from nonebot import get_app, get_bot, get_driver
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment
from pydantic import BaseModel, Field

from common.biz import result
from server.routes import router

app: FastAPI = get_app()
driver = get_driver()
app.router.include_router(router)


# 定义单个消息的模型
class SingleMessage(BaseModel):
  content: str | int = Field(..., description="消息内容")
  type: str = Field("text", description="消息类型，默认为文本消息")


@app.post("/send")
async def send_message(
  group_id: int = Form(0), user_id: int = Form(0), messages: str = Form(...), files: list[UploadFile] = File(None)
):
  bot = cast(Bot, get_bot())

  if not (group_id or user_id):
    return result.fail("请设置group_id/user_id")

  msgs: Message = Message()

  try:
    message_list: list[SingleMessage] = [SingleMessage.model_validate(msg) for msg in json.loads(messages)]
  except json.JSONDecodeError:
    return {"error": "Invalid JSON format in messages"}

  for msg in message_list:
    if msg.type == "text":
      msgs += MessageSegment.text(text=msg.content)  # type: ignore
    elif msg.type == "image":
      msgs += MessageSegment.image(file=msg.content)  # type: ignore
    elif msg.type == "at":
      msgs += MessageSegment.at(user_id=msg.content)
    elif msg.type == "reply":
      # 需要消息id
      msgs += MessageSegment.reply(id_=msg.content)  # type: ignore

  if files:
    for file in files:
      file_content = await file.read()
      if file_content:
        msgs += MessageSegment.image(file=file_content)

  if group_id:
    await send_message_to_group(bot, group_id=group_id, msgs=msgs)
  elif user_id:
    await send_message_to_user(bot, user_id=user_id, msgs=msgs)

  try:
    return result.success({}, "发送成功")
  except Exception as e:
    return result.fail(str(e))  # 确保返回字符串


async def send_message_to_group(bot: Bot, group_id: int, msgs: Message):
  await bot.send_group_msg(group_id=group_id, message=msgs)


async def send_message_to_user(bot: Bot, user_id: int, msgs: Message):
  await bot.send_private_msg(user_id=user_id, message=msgs)
