"""@用户提取"""

import re

from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.typing import T_State


def _extract_qq_numbers(text: str) -> list[int]:
  return [int(num) for num in re.findall(r"\d{1,12}", text)]


async def get_at_users(bot: Bot, event: GroupMessageEvent, state: T_State) -> list[int]:
  at_users: set[int] = set()

  if args := state.get("_prefix", {}).get("command_arg"):
    args = args.extract_plain_text().strip().split()
    at_users.update(set(_extract_qq_numbers(" ".join(args))))

  if event.is_tome():
    at_users.add(int(bot.self_id))

  if event.reply:
    return []

  for seg in event.message:
    if seg.type == "at":
      qq = seg.data.get("qq")
      if qq and qq.isdigit():
        at_users.add(int(qq))
  return list(at_users)


def Ats(min_num: int = 1, max_num: int = 99):
  async def dependency(bot: Bot, event: GroupMessageEvent, matcher: Matcher, state: T_State):
    at_users = await get_at_users(bot, event, state)
    if len(at_users) > max_num or len(at_users) < min_num:
      await matcher.finish()
    return at_users

  return Depends(dependency)


def At(required=False):
  async def dependency(bot: Bot, event: GroupMessageEvent, matcher: Matcher, state: T_State):
    at_users = await get_at_users(bot, event, state)
    if required:
      if not at_users:
        await matcher.finish("请@一个用户后再试")
      return next(iter(at_users))
    return next(iter(at_users)) if at_users else None

  return Depends(dependency)
