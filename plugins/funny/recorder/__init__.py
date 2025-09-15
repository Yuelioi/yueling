import time

from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata

from common.config import config

__plugin_meta__ = PluginMetadata(
  name="recorder",
  description="特定群友欢迎图",
  usage="定时发送",
  extra={"group": "娱乐", "hidden": True, "commands": []},
)

recorder = on_message()

# 特定群友 -> recorder
daxiaojie_last_time = 0


@recorder.handle()
async def recorder_handler(event: GroupMessageEvent):
  """特定群友图"""
  group = [444282933, 680653092]

  if event.group_id not in group:
    return

  now = time.time()

  if event.user_id == 446480506:
    global daxiaojie_last_time
    if now - daxiaojie_last_time > 3600:
      img = config.resource.images / "daxiaojie.gif"
      daxiaojie_last_time = now
      await recorder.finish(MessageSegment.image(img))
