from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.message import event_preprocessor
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from common.base.Depends import Args
from common.base.Handle import register_handler
from common.config import gv

__plugin_meta__ = PluginMetadata(
  name="关键词屏蔽",
  description="管理群组屏蔽关键词的插件。",
  usage="使用方法: 添加屏蔽[关键词] / 删除屏蔽[关键词] / 查看屏蔽",
  extra={"group": "群管", "commands": ["添加屏蔽", "删除屏蔽", "查看屏蔽", "取消屏蔽"]},
)


keywords = on_command("添加屏蔽", aliases={"删除屏蔽", "查看屏蔽", "取消屏蔽"})


@event_preprocessor
async def _(bot: Bot, event: GroupMessageEvent):
  if group_keywords := gv.group_ban_keywords.get(event.group_id, []):
    for key in group_keywords:
      if key in event.get_plaintext():
        await bot.delete_msg(message_id=event.message_id)
        break


async def _kd(event: GroupMessageEvent, args: list[str] = Args(0), cmd=RawCommand()):
  group_id = str(event.group_id)
  if cmd in ["添加屏蔽", "删除屏蔽", "取消屏蔽"]:
    if not args:
      return "请指定关键词"

    if cmd == "添加屏蔽":
      # 添加屏蔽
      group = gv.group_ban_keywords.setdefault(group_id, [])
      if not all(arg in group for arg in args):
        group.extend(arg for arg in args if arg not in group)
        gv.group_ban_keywords.save()
      return "添加屏蔽成功"

    else:
      # 取消屏蔽
      group = gv.group_ban_keywords.get(group_id, [])
      if not all(arg not in group for arg in args):
        group[:] = [arg for arg in group if arg not in args]
        gv.group_ban_keywords.save()

      return "删除屏蔽蔽成功"

  # 查看屏蔽
  group = gv.group_ban_keywords.get(str(event.group_id), [])
  if group:
    return "当前屏蔽词为: " + ", ".join(group)
  return "当前没有该屏蔽词喔"


register_handler(keywords, _kd)
