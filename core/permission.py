"""权限系统 — RBAC + 插件启用控制"""

from enum import IntEnum
from functools import partial
from pathlib import Path
from typing import Any, Awaitable, Callable, cast  # noqa

import nonebot
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent

from core.config import config
from core.store import JsonStore


def _get_driver_config():
  return nonebot.get_driver().config


# ─── Permission Levels ─────────────────────────────────────────

class PermissionLevel(IntEnum):
  BLOCKED = 0
  MEMBER = 10
  TRUSTED = 20
  ADMIN = 30
  OWNER = 40
  SUPERUSER = 50


# ─── Permission Manager ───────────────────────────────────────

class PermissionManager:
  def __init__(self):
    self._plugin_states = JsonStore(config.paths.database / "plugin_states.json")
    self._user_blocks = JsonStore(config.paths.database / "user_plugin_blocks.json")

  def get_level(self, user_id: int, role: str = "member") -> PermissionLevel:
    if str(user_id) in _get_driver_config().superusers:
      return PermissionLevel.SUPERUSER
    match role:
      case "owner":
        return PermissionLevel.OWNER
      case "admin":
        return PermissionLevel.ADMIN
      case _:
        return PermissionLevel.MEMBER

  async def get_level_from_event(self, bot: Bot, event: GroupMessageEvent) -> PermissionLevel:
    user_id = event.user_id
    if str(user_id) in _get_driver_config().superusers:
      return PermissionLevel.SUPERUSER
    try:
      info = await bot.get_group_member_info(group_id=event.group_id, user_id=user_id)
      role = info.get("role", "member")
    except Exception:
      role = "member"
    return self.get_level(user_id, role)

  def is_plugin_enabled(self, plugin_name: str, group_id: int) -> bool:
    states = self._plugin_states.get(str(group_id), {})
    return states.get(plugin_name, True)

  def enable_plugin(self, plugin_name: str, group_id: int):
    states = self._plugin_states.get(str(group_id), {})
    states[plugin_name] = True
    self._plugin_states.set(str(group_id), states)

  def disable_plugin(self, plugin_name: str, group_id: int):
    states = self._plugin_states.get(str(group_id), {})
    states[plugin_name] = False
    self._plugin_states.set(str(group_id), states)

  def is_user_blocked(self, plugin_name: str, user_id: int) -> bool:
    blocked = self._user_blocks.get(str(user_id), [])
    return plugin_name in blocked

  def block_user_plugin(self, plugin_name: str, user_id: int):
    blocked = self._user_blocks.get(str(user_id), [])
    if plugin_name not in blocked:
      blocked.append(plugin_name)
      self._user_blocks.set(str(user_id), blocked)

  def unblock_user_plugin(self, plugin_name: str, user_id: int):
    blocked = self._user_blocks.get(str(user_id), [])
    if plugin_name in blocked:
      blocked.remove(plugin_name)
      self._user_blocks.set(str(user_id), blocked)


permission_manager = PermissionManager()


# ─── Legacy compat layer ──────────────────────────────────────


class PermissionChecker:
  def __init__(self, checker_func: Callable[[Any, Any, Any, Any], Awaitable[bool]], _pass=False):
    self.checker_func = checker_func
    self._pass = _pass

  async def __call__(self, event, bot, state, arp) -> bool:
    return await self.checker_func(event, bot, state, arp)

  async def and_check(self, event, bot, state, arp) -> bool:
    return await self.checker_func(event, bot, state, arp)

  def __and__(self, other: "PermissionChecker") -> "PermissionChecker":
    return PermissionChecker(partial(self._combined_checker_and, other))

  async def _combined_checker_and(self, other: "PermissionChecker", event, bot, state, arp) -> bool:
    return await self.and_check(event, bot, state, arp) and await other.and_check(event, bot, state, arp)


def skip_admin_check(bot: Bot, event: Event):
  if isinstance(event, PrivateMessageEvent):
    return True
  return False


async def get_user_role(bot: Bot, group_id: int, user_id: int) -> str:
  bot_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
  return bot_info.get("role") or ""


async def admin_validate(bot: Bot, group_id: int, user_id: int) -> bool:
  role = await get_user_role(bot, group_id, user_id)
  return role in ["admin", "owner"]


def is_superuser(event: GroupMessageEvent) -> bool:
  return str(event.user_id) in _get_driver_config().superusers


async def is_admin(bot: Bot, event: GroupMessageEvent) -> bool:
  return await admin_validate(bot=bot, group_id=event.group_id, user_id=event.user_id) or event.user_id in _get_driver_config().superusers


async def is_bot_admin(bot: Bot, event: GroupMessageEvent) -> bool:
  return await admin_validate(bot=bot, group_id=event.group_id, user_id=int(bot.self_id))


# Deprecated aliases
Superuser_validate = is_superuser
User_admin_validate = is_admin
Bot_admin_validate = is_bot_admin
