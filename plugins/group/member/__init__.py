import json

import aiofiles
from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata

from common.config import gv
from plugins.group.member.models import MemberInfo

WorkingMessage = "正在处理中/未知错误"


__plugin_meta__ = PluginMetadata(
  name="群成员管理",
  description="群友备份",
  usage="""群友备份/备份群友""",
  extra={"group": "群管", "commands": ["群友备份", "备份群友"]},
)

member = on_fullmatch(("群友备份", "备份群友"))


async def write(file, data: dict):
  async with aiofiles.open(file, mode="w", encoding="utf-8") as f:
    updated_data = json.dumps(data, ensure_ascii=False, indent=4)
    await f.write(updated_data)


@member.handle()
async def backup_members(bot: Bot, event: GroupMessageEvent):
  member_infos: list[MemberInfo] = await bot.get_group_member_list(group_id=event.group_id, no_cache=True)  # type: ignore
  group_id = str(event.group_id)

  members = []

  for member_info in member_infos:
    members.append(
      {
        "group_id": member_info["group_id"],
        "user_id": member_info["user_id"],
        "nickname": member_info["nickname"],
        "card": member_info["card"],
        "last_sent_time": member_info["last_sent_time"],
      }
    )

  gv.group_members[group_id] = members
  gv.group_members.save()

  await member.finish("群友备份成功")
