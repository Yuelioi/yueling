"""AI 内置工具 — 上下文感知（聊天记录、用户解析、头像、群成员）"""

import io

from ai.registry import tool
from ai.session import session_manager
from core.context import ToolContext
from services.qq_api import download_avatar


@tool(
  tags=["context"],
  examples=["刚才谁说了什么", "上面说的是谁", "最近聊天记录"],
)
async def get_chat_history(ctx: ToolContext, count: int = 15) -> str:
  """获取群最近聊天记录，用于理解上下文和确定发言者身份

  Args:
    count: 获取条数(1-30)
  """
  count = max(1, min(30, count))
  try:
    history = await ctx.bot.call_api(
      "get_group_msg_history", group_id=ctx.group_id,
      message_id=str(ctx.event.message_id), count=count,
    )
    messages = history.get("messages", []) if history else []
    if not messages:
      return "无记录"
    lines = []
    for msg in messages[-count:]:
      uid = msg.get("user_id", 0)
      nick = msg.get("sender", {}).get("card") or msg.get("sender", {}).get("nickname", "?")
      parts = []
      for seg in msg.get("message", []):
        if seg["type"] == "text" and seg["data"].get("text", "").strip():
          parts.append(seg["data"]["text"].strip())
        elif seg["type"] == "image":
          parts.append("[图片]")
        elif seg["type"] == "at":
          parts.append(f"[@{seg['data'].get('qq')}]")
      if parts:
        lines.append(f"{nick}({uid}): {' '.join(parts)}")
    return "\n".join(lines)
  except Exception as e:
    return f"获取失败: {e}"


@tool(
  tags=["context", "group"],
  examples=["禁言张三", "查一下小明", "那个xxx是谁"],
)
async def resolve_user_by_name(ctx: ToolContext, name: str) -> str:
  """通过昵称/群名片模糊匹配查找用户QQ号

  Args:
    name: 昵称或群名片关键词
  """
  try:
    members = await ctx.bot.get_group_member_list(group_id=ctx.group_id)
    matches = []
    for m in members:
      card = m.get("card", "")
      nickname = m.get("nickname", "")
      if name in card or name in nickname:
        display = card or nickname
        matches.append(f"{display} → {m['user_id']}")
    if not matches:
      return f"未找到包含'{name}'的群成员"
    return "\n".join(matches[:5])
  except Exception as e:
    return f"查找失败: {e}"


@tool(
  tags=["context", "image"],
  examples=["用他的头像", "拿一下头像做图"],
)
async def fetch_avatar(ctx: ToolContext, user: int = 0) -> str:
  """获取用户头像数据存入上下文，供后续绘图/合成工具使用

  Args:
    user: QQ号，0=发言者自己
  """
  target = user or ctx.user_id
  try:
    img = await download_avatar(target)
    if img and isinstance(img, io.BytesIO):
      session = session_manager.get(ctx.group_id, ctx.user_id)
      session.tool_state[f"avatar_{target}"] = img.getvalue()
      return f"已获取 {target} 的头像（{len(img.getvalue())}字节，已存入上下文）"
    return "获取头像失败"
  except Exception:
    return "获取头像失败"


@tool(
  tags=["context", "group"],
  examples=["群里有没有叫xxx的", "这个人在群里吗", "群里谁是管理"],
)
async def get_group_members(ctx: ToolContext, keyword: str = "") -> str:
  """获取群成员列表，可按关键词筛选，用于确认成员身份

  Args:
    keyword: 搜索关键词，空=返回最近活跃成员
  """
  try:
    members = await ctx.bot.get_group_member_list(group_id=ctx.group_id)
    if keyword:
      members = [m for m in members if keyword in (m.get("card", "") + m.get("nickname", ""))]
    if not members:
      return "无匹配成员"
    members.sort(key=lambda m: m.get("last_sent_time", 0), reverse=True)
    lines = []
    for m in members[:15]:
      name = m.get("card") or m.get("nickname", "?")
      role = m.get("role", "member")
      tag = " [管理]" if role == "admin" else " [群主]" if role == "owner" else ""
      lines.append(f"{name}({m['user_id']}){tag}")
    if len(members) > 15:
      lines.append(f"... 共{len(members)}人")
    return "\n".join(lines)
  except Exception as e:
    return f"获取失败: {e}"
