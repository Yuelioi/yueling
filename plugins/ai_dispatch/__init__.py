"""AI 调度 NoneBot 入口插件 — 监听 @bot 消息并分发到 AI 工具系统"""

import nonebot
from nonebot import get_driver, logger, on_message
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me

from ai.dispatcher import dispatch
from ai.guard import guard_check
from ai.scanner import scan_plugins_for_tools
from ai.trace import start_trace
from core.context import ToolContext
import ai.tools  # noqa: F401

__plugin_meta__ = PluginMetadata(
  name="AI调度",
  description="自然语言指令调度",
  usage="@月灵 + 自然语言",
  extra={"group": "系统", "hidden": True, "commands": []},
)


@get_driver().on_startup
async def _register_plugin_tools():
  scan_plugins_for_tools()
  logger.info(f"AI tools registered: {len(__import__('ai.registry', fromlist=['registry']).registry.get_all())}")


ai_handler = on_message(rule=to_me(), priority=0, block=True)


@ai_handler.handle()
async def handle_ai(bot: Bot, event: GroupMessageEvent):

  text = event.get_plaintext().strip()
  if not text:
    return

  start_trace()
  logger.info(f"AI调度: '{text}' from {event.user_id}")

  driver_config = nonebot.get_driver().config
  user_role = "member"
  if str(event.user_id) in driver_config.superusers:
    user_role = "superuser"
  else:
    try:
      info = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id)
      role = info.get("role", "member")
      if role in ("admin", "owner"):
        user_role = role
    except Exception:
      pass

  guard_result = guard_check(text, user_role)
  if guard_result:
    await ai_handler.finish(guard_result)

  ctx = ToolContext(
    user_id=event.user_id,
    group_id=event.group_id,
    role=user_role,
    bot=bot,
    event=event,
  )

  try:
    result = await dispatch(text, ctx)
    if result:
      await ai_handler.finish(result)
  except FinishedException:
    raise
  except Exception as e:
    logger.error(f"AI调度异常: {e}")
    await ai_handler.finish("AI 处理出错了")
