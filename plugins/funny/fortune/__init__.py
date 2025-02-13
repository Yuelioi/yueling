"""
fork:https://github.com/MinatoAquaCrews/nonebot_plugin_fortune
__fortune_version__ = "v0.4.10.post2"
"""

from nonebot.adapters import Event
from nonebot.log import logger
from nonebot_plugin_alconna import Alconna, Args, MsgTarget, UniMessage, on_alconna
from nonebot_plugin_apscheduler import scheduler

from common.Alc.Alc import fullmatch, pm, ptc
from plugins.funny.fortune.consts import FORTUNE_THEMES
from plugins.funny.fortune.data_source import FortuneManager, fortune_manager

__plugin_meta__ = pm(
  name="今日运势",
  description="来看看今天的运势吧！",
  usage="""今日运势/抽签/运势""",
  group="娱乐",
)


_fortune = Alconna("今日运势", Args["theme?", str], meta=ptc(__plugin_meta__))
fortune = on_alconna(_fortune, priority=5, block=True, aliases={"抽签", "运势"})


_theme = fullmatch("抽签主题")
themes = on_alconna(_theme)


@themes.handle()
async def _():
  file_names = [file.stem for file in FORTUNE_THEMES.iterdir() if file.is_dir()]
  await themes.finish("/".join(file_names))


@fortune.handle()
async def fortune_divine(event: Event, target: MsgTarget, theme: str = ""):
  if theme == "主题":
    return
  uid: str = str(event.get_user_id())
  is_first, image_file = fortune_manager.divine(uid, theme)
  if image_file is None:
    return "今日运势生成出错……"
  if not is_first:
    msg = UniMessage.text("你今天抽过签了，再给你看一次哦🤗\n") + UniMessage.image(path=image_file)
  else:
    logger.info(f"User {uid} | Group {target.id} 占卜了今日运势")
    msg = UniMessage.text("✨今日运势✨\n") + UniMessage.image(path=image_file)
  res = msg + UniMessage.at(uid)
  await fortune.finish(res)


# 清空昨日生成的图片
@scheduler.scheduled_job("cron", hour=0, minute=0, misfire_grace_time=60)
async def _():
  FortuneManager.clean_out_pics()
  logger.info("昨日运势图片已清空！")
