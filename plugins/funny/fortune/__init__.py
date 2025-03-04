"""
fork:https://github.com/MinatoAquaCrews/nonebot_plugin_fortune
__fortune_version__ = "v0.4.10.post2"
"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import scheduler

from common.base.Depends import Arg
from plugins.funny.fortune.data_source import FortuneManager, fortune_manager

__plugin_meta__ = PluginMetadata(
  name="今日运势",
  description="来看看今天的运势吧！",
  usage="""今日运势/抽签/运势""",
  extra={"group": "娱乐"},
)


fortune = on_command(cmd="今日运势", aliases={"抽签", "运势"})


@fortune.handle()
async def fortune_divine(event: GroupMessageEvent, theme=Arg()):
  uid: str = str(event.get_user_id())
  is_first, image_file = fortune_manager.divine(uid, theme)
  if image_file is None:
    return "今日运势生成出错……"
  if not is_first:
    msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(file=image_file)
  else:
    logger.info(f"User {uid} | Group {event.get_user_id()} 占卜了今日运势")
    msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(file=image_file)
  res = msg + MessageSegment.at(uid)
  await fortune.finish(res)


# 清空昨日生成的图片
@scheduler.scheduled_job("cron", hour=0, minute=0, misfire_grace_time=60)
async def _():
  FortuneManager.clean_out_pics()
  logger.info("昨日运势图片已清空！")
