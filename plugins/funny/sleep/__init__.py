import random

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata

from core.permission import is_bot_admin, is_admin

__plugin_meta__ = PluginMetadata(
  name="我要睡觉",
  description="别水群了, 赶紧睡觉, 强制睡眠",
  usage="""我要睡觉""",
  extra={"group": "娱乐", "commands": ["我要睡觉"]},
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
async def sleep_handle(bot: Bot, event: GroupMessageEvent):
  sleep_time = random.randint(5, 8)
  sleep_word = sleep_words[random.randint(0, len(sleep_words) - 1)]

  userinfo = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)

  if await is_bot_admin(bot, event) and not await is_admin(bot, event):
    await bot.set_group_ban(
      group_id=event.group_id,
      user_id=event.user_id,
      duration=sleep_time * 60 * 60,
    )
  await sleep.finish(f"{userinfo['nickname']}{sleep_word},{sleep_time}小时后见!")
