import time

from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot_plugin_alconna import on_alconna

from common.Alc.Alc import msg, pm, ptc
from common.config import config

__plugin_meta__ = pm(
  name="recorder",
  description="特定群友欢迎图",
  usage="定时发送",
  group="funny",
  hidden=True,
)
_recorder = msg()
_recorder.meta = ptc(__plugin_meta__)
recorder = on_alconna(_recorder)

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
