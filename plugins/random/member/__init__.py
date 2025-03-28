import random

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata

from common.base.Handle import register_handler

__plugin_meta__ = PluginMetadata(
  name="随机群友",
  description="随机抽群友",
  usage="""抽群友/来点群友/抽xx群友/抽男群友/抽老婆/抽老公""",
  extra={"group": "随机", "commands": ["抽群友"]},
)


member = on_regex("抽(.*)群友(.*)|随机.*群友.*|来个.*群友.*|来点.*群友.*")


async def random_member(bot: Bot, event: GroupMessageEvent):
  user = event.get_user_id()
  group_info = await bot.get_group_member_list(group_id=event.group_id, no_cache=True)  # type: ignore

  limit = 25

  group_info = sorted(group_info, key=lambda x: x["last_sent_time"])[-limit:]

  member_info = random.choice(group_info)
  user_id, nickname = member_info["user_id"], member_info["nickname"]

  msg = MessageSegment.at(int(user))
  msg += MessageSegment.text(f"你抽到的是:{nickname}\n")
  msg += MessageSegment.image(f"https://q.qlogo.cn/headimg_dl?dst_uin={user_id}&spec=640")

  whitelist = [913322478, 48896449]
  if int(user_id) in whitelist:
    msg += MessageSegment.at(int(user_id))

  return msg


register_handler(member, random_member)
