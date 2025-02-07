import random

from nonebot.adapters import Bot
from nonebot_plugin_alconna import MsgTarget, on_alconna
from nonebot_plugin_userinfo import EventUserInfo, UserInfo

from common.Alc.Alc import fullmatch, pm, ptc, register_handler
from common.Alc.Permission import Bot_Checker

__plugin_meta__ = pm(
  name="我要睡觉",
  description="别水群了, 赶紧睡觉, 强制睡眠",
  usage="""我要睡觉""",
  group="娱乐",
)

_sleep = fullmatch("我要睡觉")
_sleep.meta = ptc(__plugin_meta__)
sleep = on_alconna(_sleep)


sleep_words = [
  "被梦魇抓走了",
  "被僵尸吃掉了脑子",
  "被外星人抓走做实验了",
  "去梦里拯救世界了",
]


@sleep.assign("$main", additional=Bot_Checker)
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


register_handler(sleep, sleep_handle)
