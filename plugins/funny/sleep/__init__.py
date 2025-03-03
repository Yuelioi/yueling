import random

from nonebot import on_fullmatch
from nonebot.adapters import Bot
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import MsgTarget
from nonebot_plugin_userinfo import EventUserInfo, UserInfo

__plugin_meta__ = PluginMetadata(
  name="我要睡觉",
  description="别水群了, 赶紧睡觉, 强制睡眠",
  usage="""我要睡觉""",
  extra={
    "group": "娱乐",
  },
)

sleep = on_fullmatch("我要睡觉")


sleep_words = [
  "被梦魇抓走了",
  "被僵尸吃掉了脑子",
  "被外星人抓走做实验了",
  "去梦里拯救世界了",
]


# TODO 权限验证
@sleep.handle()
async def sleep_handle(bot: Bot, target: MsgTarget, user_info: UserInfo = EventUserInfo()):
  if target.private:
    return

  sleep_time = random.randint(5, 8)
  sleep_word = sleep_words[random.randint(0, len(sleep_words) - 1)]

  username = user_info.user_name
  await bot.set_group_ban(
    group_id=target.id,
    user_id=user_info.user_id,
    duration=sleep_time * 60 * 60,
  )
  await sleep.finish(f"{username}{sleep_word},{sleep_time}小时后见!")
