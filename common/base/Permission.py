from functools import partial
from typing import Any, Awaitable, Callable, cast  # noqa

import nonebot
from nonebot.adapters import Bot, Event
from nonebot.adapters.discord import Bot as DiscordBot
from nonebot.adapters.discord.event import MessageEvent as DiscordEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.permission import Permission

config = nonebot.get_driver().config


class PermissionChecker:
  def __init__(self, checker_func: Callable[[Any, Any, Any, Any], Awaitable[bool]], _pass=False):
    self.checker_func = checker_func
    self._pass = _pass

  async def __call__(self, event, bot, state, arp) -> bool:
    result = await self.checker_func(event, bot, state, arp)
    return result

  async def and_check(self, event, bot, state, arp) -> bool:
    result = await self.checker_func(event, bot, state, arp)

    return result

  def __and__(self, other: "PermissionChecker") -> "PermissionChecker":
    return PermissionChecker(partial(self._combined_checker_and, other))

  async def _combined_checker_and(self, other: "PermissionChecker", event, bot, state, arp) -> bool:
    return await self.and_check(event, bot, state, arp) and await other.and_check(event, bot, state, arp)


def skip_admin_check(bot: Bot, event: Event):
  """跳过权限验证"""
  if isinstance(event, DiscordEvent) and isinstance(bot, DiscordBot):
    return True
  if isinstance(event, PrivateMessageEvent):
    return True
  return False


async def get_user_role(bot: Bot, group_id: int, user_id: int) -> str:
  """QQ群获取用户角色"""
  bot_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
  return bot_info.get("role") or ""


async def admin_validate(bot: Bot, group_id: int, user_id: int) -> bool:
  """判断QQ群用户是否为管理员"""
  role = await get_user_role(bot, group_id, user_id)
  return role in ["admin", "owner"]


def Superuser_validate(event: GroupMessageEvent) -> bool:
  """判断用户是否为超级用户"""
  return event.user_id in config.superusers


async def User_admin_validate(bot: Bot, event: GroupMessageEvent) -> bool:
  """判断QQ群用户是否为管理员或超级用户"""
  return await admin_validate(bot=bot, group_id=event.group_id, user_id=event.user_id) or event.user_id in config.superusers


async def Bot_admin_validate(bot: Bot, event: GroupMessageEvent) -> bool:
  """判断机器人是否为群管理员"""

  return await admin_validate(bot=bot, group_id=event.group_id, user_id=int(bot.self_id))
