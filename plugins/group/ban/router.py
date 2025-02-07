from fastapi import APIRouter
from nonebot import get_bot

trace_moe = APIRouter()
from common.biz import result


@trace_moe.post("/ban", response_model=dict)
async def ban(group_id: int, user_id: int, duration: int):
  if user_id == 435826135:
    return result.success({"message": "大胆妖孽! 你想对我爹做什么!"})
  bot = get_bot()
  await bot.set_group_ban(
    group_id=group_id,
    user_id=user_id,
    duration=duration * 60,
  )

  return result.success({"message": "禁言成功"})
