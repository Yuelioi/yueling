from typing import cast

import nonebot
from nonebot.adapters import Bot, Event
from nonebot.adapters.discord import Bot as DiscordBot
from nonebot.adapters.discord.event import MessageEvent as DiscordEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent

config = nonebot.get_driver().config


def skip_admin_check(bot: Bot, event: Event):
  """跳过权限验证"""
  if isinstance(event, DiscordEvent) and isinstance(bot, DiscordBot):
    return True
  if isinstance(event, PrivateMessageEvent):
    return True
  return False


def Superuser_validate(user_id: int) -> bool:
  """判断用户是否为超级用户"""
  return user_id in config.superusers


async def get_user_role(bot: Bot, group_id: int, user_id: int) -> str:
  """QQ群获取用户角色"""
  bot_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
  return bot_info.get("role") or ""


async def admin_validate(bot: Bot, group_id: int, user_id: int) -> bool:
  """判断QQ群用户是否为管理员"""
  if isinstance(bot, DiscordBot):
    return True
  role = await get_user_role(bot, group_id, user_id)
  return role in ["admin", "owner"]


async def User_admin_validate(bot: Bot, event: Event) -> bool:
  """判断QQ群用户是否为管理员或超级用户
  discord:True
  """
  if skip_admin_check(bot, event):
    return True
  qqEvent = cast(GroupMessageEvent, event)
  return await admin_validate(bot=bot, group_id=qqEvent.group_id, user_id=qqEvent.user_id) or qqEvent.user_id in config.superusers


async def Bot_admin_validate(bot: Bot, event: Event) -> bool:
  """判断机器人是否为群管理员
  discord:True
  """
  if skip_admin_check(bot, event):
    return True

  qqEvent = cast(GroupMessageEvent, event)

  return await admin_validate(bot=bot, group_id=qqEvent.group_id, user_id=int(bot.self_id))
