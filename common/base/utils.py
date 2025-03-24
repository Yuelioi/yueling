from typing import Literal, TypedDict

from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent


class GroupMemberInfo(TypedDict):
  """QQ 群成员信息字典类型定义（带类型验证）"""

  group_id: int
  user_id: int
  nickname: str
  card: str
  sex: str
  age: int
  area: str
  join_time: int
  last_sent_time: int
  level: str
  role: Literal["owner", "admin", "member"]  # 限定角色取值范围
  unfriendly: bool
  title: str
  title_expire_time: int
  card_changeable: bool


async def get_user_info(bot: Bot, event: GroupMessageEvent) -> GroupMemberInfo:
  userinfo = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
  return userinfo
