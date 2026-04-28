"""命令参数提取"""

from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.typing import T_State


def get_command_args(state: T_State):
  if args := state.get("_prefix", {}).get("command_arg"):
    command: str = args.extract_plain_text()
    _args = command.strip().split()
    return _args
  return []


def Args(min_num: int = 1, max_num: int = 999):
  async def dependency(matcher: Matcher, state: T_State):
    args = get_command_args(state)
    if len(args) > max_num or len(args) < min_num:
      await matcher.finish()
    return args

  return Depends(dependency)


def Arg(required=False):
  async def dependency(matcher: Matcher, state: T_State):
    args = get_command_args(state)
    if args:
      return args[0]
    if required:
      await matcher.finish()
    return ""

  return Depends(dependency)
