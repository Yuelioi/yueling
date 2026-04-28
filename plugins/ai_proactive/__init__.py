"""主动发言 NoneBot 插件 — 监听群消息，积分触发主动参与 + 消息统计"""

import asyncio
import random
import time

from nonebot import on_message, logger
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import scheduler
from sqlalchemy import delete

from ai.proactive import proactive_manager
from core.database import async_session
from models.message_stat import MessageStat

__plugin_meta__ = PluginMetadata(
  name="主动发言",
  description="AI主动参与群聊",
  usage="自动触发，无需命令",
  extra={"group": "系统", "hidden": True, "commands": []},
)

proactive_listener = on_message(priority=99, block=False)


@proactive_listener.handle()
async def handle_proactive(bot: Bot, event: GroupMessageEvent):
  text = event.get_plaintext().strip()

  nick = event.sender.card or event.sender.nickname or str(event.user_id)
  try:
    async with async_session() as session:
      session.add(MessageStat(
        group_id=event.group_id,
        user_id=event.user_id,
        nickname=nick,
        timestamp=time.time(),
      ))
      await session.commit()
  except Exception:
    pass

  if event.is_tome() or not text:
    return

  proactive_manager.feed_message(event.group_id, event.user_id, text)

  if not proactive_manager.should_speak(event.group_id):
    return

  proactive_manager.record_speak(event.group_id)
  delay = random.uniform(1.5, 4.0)
  await asyncio.sleep(delay)

  context = proactive_manager.get_recent_context(event.group_id)
  if not context:
    return

  try:
    from ai.llm import llm_complete
    reply = await llm_complete(
      "你是月灵，一个12岁的QQ群助手机器人。"
      "你正在旁观群聊，觉得可以插一句话。"
      "规则：回复简短(10-30字)、自然、不突兀、有趣或有用。"
      "如果没什么好说的就回复空字符串。",
      f"最近的群聊内容:\n{context}\n\n你想说点什么？",
      temperature=1.0,
      max_tokens=60,
    )
    reply = reply.strip()
    if reply and len(reply) > 1:
      await bot.send_group_msg(group_id=event.group_id, message=reply)
  except Exception as e:
    logger.debug(f"Proactive speak failed: {e}")


@scheduler.scheduled_job("cron", hour=4, minute=0, misfire_grace_time=300)
async def _cleanup_old_stats():
  cutoff = time.time() - 30 * 86400
  try:
    async with async_session() as session:
      await session.execute(delete(MessageStat).where(MessageStat.timestamp < cutoff))
      await session.commit()
    logger.info("Cleaned up message_stats older than 30 days")
  except Exception as e:
    logger.debug(f"message_stats cleanup failed: {e}")
