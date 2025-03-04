from functools import partial
from typing import Any, Awaitable, Callable  # noqa

from common.config.message import BotIsNotAdmin, UserIsNotAdmin, UserIsNotSuperAdmin


class PermissionChecker:
  def __init__(self, checker_func: Callable[[Any, Any, Any, Any], Awaitable[bool]], error_message: str, _pass=False):
    self.checker_func = checker_func
    self.error_message = error_message
    self._pass = _pass

  async def __call__(self, event, bot, state, arp) -> bool:
    result = await self.checker_func(event, bot, state, arp)
    if not result:
      if not self._pass:
        await bot.send(event, self.error_message)
    return result

  async def and_check(self, event, bot, state, arp) -> bool:
    result = await self.checker_func(event, bot, state, arp)
    if not result:
      await bot.send(event, self.error_message)
    return result

  def __and__(self, other: "PermissionChecker") -> "PermissionChecker":
    return PermissionChecker(partial(self._combined_checker_and, other), "", True)

  async def _combined_checker_and(self, other: "PermissionChecker", event, bot, state, arp) -> bool:
    return await self.and_check(event, bot, state, arp) and await other.and_check(event, bot, state, arp)


async def user_admin_check(event, bot, state, arp):
  """用户管理员权限检查"""
  return True


async def bot_admin_check(event, bot, state, arp):
  """机器人管理员权限检查"""
  return True


async def superuser_check(event, bot, state, arp):
  """超级用户权限检查"""
  return True


Superuser_Checker = PermissionChecker(superuser_check, UserIsNotSuperAdmin)
User_Checker = PermissionChecker(user_admin_check, UserIsNotAdmin)
Bot_Checker = PermissionChecker(bot_admin_check, BotIsNotAdmin)
