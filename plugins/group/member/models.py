from typing import TypedDict


class MemberInfo(TypedDict):
  group_id: int
  user_id: int
  nickname: str
  card: str
  sex: str  # "male", "female", or "unknown"
  age: int
  area: str
  join_time: int
  last_sent_time: int
  level: str
  role: str  # "owner", "admin", or "member"
  unfriendly: bool
  title: str
  title_expire_time: int
  card_changeable: bool
  shut_up_timestamp: int
