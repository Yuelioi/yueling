"""工具执行引擎 — 参数解析 + 业务校验 + 执行"""

import inspect

from nonebot import logger

from ai.registry import ToolMeta, registry
from core.context import ToolContext
from core.errors import InvalidInput, ToolExecutionError


MEMBER_CHECK_TOOLS = {"ban_user", "mute_user", "kick_user"}
RECENT_SPEAKER_TOOLS = {"ban_user"}


def _filter_args(meta: ToolMeta, args: dict) -> dict:
  """只保留工具函数实际接受的参数，丢弃 LLM 传的多余字段"""
  if not meta.func:
    return args
  sig = inspect.signature(meta.func)
  valid_params = set(sig.parameters.keys()) - {"ctx", "self"}
  return {k: v for k, v in args.items() if k in valid_params}


async def validate_args(meta: ToolMeta, args: dict, ctx: ToolContext) -> None:
  if meta.name in MEMBER_CHECK_TOOLS and "user" in args:
    target = args["user"]
    if isinstance(target, int):
      members = await ctx.bot.get_group_member_list(group_id=ctx.group_id)
      member_ids = {m["user_id"] for m in members}
      if target not in member_ids:
        raise InvalidInput(f"用户 {target} 不在本群")

  if meta.name in RECENT_SPEAKER_TOOLS and "user" in args:
    target = args["user"]
    if isinstance(target, int):
      recent = await ctx.get_recent_speakers(20)
      if target not in recent:
        raise InvalidInput("只能对最近活跃的群成员执行此操作")

  if "duration" in args:
    duration = args.get("duration")
    if isinstance(duration, int) and duration > 43200:
      raise InvalidInput("时长不能超过 30 天")


async def execute_tool(tool_name: str, args: dict, ctx: ToolContext) -> str:
  meta = registry.get_by_name(tool_name)
  if not meta or not meta.func:
    return f"ERROR:未知工具 {tool_name}"

  if "user" in args and isinstance(args["user"], (str, int)):
    try:
      args["user"] = await ctx.resolve_user(args["user"])
    except (ValueError, InvalidInput) as e:
      return f"ERROR:{e}"

  # 过滤多余参数（LLM 可能传工具不接受的字段）
  args = _filter_args(meta, args)

  try:
    await validate_args(meta, args, ctx)
  except InvalidInput as e:
    return f"ERROR:{e.message}"

  try:
    result = await meta.func(ctx=ctx, **args)
    if result is None:
      return "执行完成"
    return str(result)
  except InvalidInput as e:
    return f"ERROR:{e.message}"
  except TypeError as e:
    return f"ERROR:参数错误 - {e}"
  except Exception as e:
    logger.error(f"Tool {tool_name} execution error: {e}")
    return f"ERROR:工具执行失败 - {e}"

