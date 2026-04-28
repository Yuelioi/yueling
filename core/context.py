from dataclasses import dataclass

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent


def extract_images(event: GroupMessageEvent) -> list[str]:
  """从消息和回复中提取所有图片 URL"""
  imgs = []
  for seg in event.message:
    if seg.type == "image":
      imgs.append(seg.data.get("url", seg.data.get("file", "")))
  if event.reply:
    for seg in event.reply.message:
      if seg.type == "image":
        imgs.append(seg.data.get("url", seg.data.get("file", "")))
  return [u for u in imgs if u]


@dataclass
class ToolContext:
  user_id: int
  group_id: int
  role: str
  bot: Bot
  event: GroupMessageEvent

  def get_images(self) -> list[str]:
    """获取消息中的图片 URL 列表"""
    return extract_images(self.event)

  async def resolve_user(self, ref: str | int) -> int:
    if isinstance(ref, int):
      return ref
    if isinstance(ref, str) and ref.isdigit():
      return int(ref)

    for seg in self.event.message:
      if seg.type == "at":
        return int(seg.data["qq"])

    members = await self.bot.get_group_member_list(group_id=self.group_id)
    for m in members:
      if ref in (m.get("card", ""), m.get("nickname", "")):
        return m["user_id"]

    raise ValueError(f"无法识别用户: {ref}")

  async def get_recent_speakers(self, limit: int = 20) -> list[int]:
    try:
      history = await self.bot.call_api(
        "get_group_msg_history", group_id=self.group_id, count=limit
      )
      messages = history.get("messages", [])
      seen = []
      for msg in reversed(messages):
        uid = msg.get("user_id")
        if uid and uid not in seen:
          seen.append(uid)
      return seen
    except Exception:
      return []
