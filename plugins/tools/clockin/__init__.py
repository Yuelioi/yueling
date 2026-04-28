import re

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata

from core.handler import register_handler
from repositories.record_repo import record_repo

__plugin_meta__ = PluginMetadata(
  name="打卡",
  description="每日打卡",
  usage="""打卡  """,
  extra={"group": "工具", "commands": ["打卡"]},
)


clock_in = on_fullmatch("打卡")


def split_string(string):
  match = re.search(r"(.+?)(\d+)$", string)
  if match:
    return match.group(1), int(match.group(2))
  return None, None


async def clock_in_handle(bot: Bot, event: GroupMessageEvent):
  user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id, no_cache=True)

  success = await record_repo.clock_in(event.user_id)
  if not success:
    return "今天打过卡了,明天再来吧~"

  if group_name := user_info.get("card"):
    pre, suf = split_string(group_name)
    if pre is not None and suf is not None:
      new_name = pre + str(suf + 1)
      await bot.set_group_card(group_id=event.group_id, user_id=event.user_id, card=new_name)

  return "打卡成功!"


register_handler(clock_in, clock_in_handle)
