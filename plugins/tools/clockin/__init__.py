import re

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata

from common.base.Handle import register_handler
from common.database.RecordManager import Record, rcm

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

  rc = Record(qq=event.user_id)
  if not rcm.check_record(rc):
    return "今天打过卡了,明天再来吧~"

  if rcm.insert_data(rc):
    res = rcm.get_records_for_current_month(rc)
    if group_name := user_info.get("card"):
      pre, suf = split_string(group_name)
      if pre is not None and suf is not None:
        new_name = pre + str(suf + 1)
        await bot.set_group_card(group_id=event.group_id, user_id=event.user_id, card=new_name)

    return f"打卡成功! 本月共打卡{len(res)}次!"
  return "打卡失败! 请联系管理员"


register_handler(clock_in, clock_in_handle)
