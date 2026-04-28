"""主动发言 NoneBot 插件 — 监听群消息，条件满足时自动参与"""

import asyncio
import random

from nonebot import on_message, logger
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata

from ai.chat import chat_fallback
from ai.proactive import proactive_manager

__plugin_meta__ = PluginMetadata(
  name="主动发言",
  description="AI主动参与群聊",
  usage="自动触发，无需命令",
  extra={"group": "系统", "hidden": True, "commands": []},
)

proactive_listener = on_message(priority=99, block=False)


@proactive_listener.handle()
async def handle_proactive(bot: Bot, event: GroupMessageEvent):
  if event.is_tome():
    return

  text = event.get_plaintext().strip()
  if not text:
    return

  proactive_manager.feed_message(event.group_id, event.user_id, text)

  if not proactive_manager.should_speak(event.group_id, int(bot.self_id)):
    return

  proactive_manager.record_speak(event.group_id)
  delay = random.uniform(2.0, 5.0)
  await asyncio.sleep(delay)

  try:
    reply = await chat_fallback(text, bot, event)
    if reply and reply != "...":
      await bot.send_group_msg(group_id=event.group_id, message=reply)
  except Exception as e:
    logger.debug(f"Proactive speak failed: {e}")
