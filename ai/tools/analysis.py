"""AI 内置工具 — 聊天分析（总结、统计）"""

import time

from sqlalchemy import select, func

from ai.llm import llm_complete
from ai.registry import ai_tool
from core.context import ToolContext
from core.database import async_session
from models.message_stat import MessageStat


def _parse_qq_messages(messages: list[dict], include_uid: bool = False) -> list[str]:
  lines = []
  for msg in messages:
    nick = msg.get("sender", {}).get("card") or msg.get("sender", {}).get("nickname", "?")
    uid = msg.get("user_id", 0)
    parts = []
    for seg in msg.get("message", []):
      if seg["type"] == "text" and seg["data"].get("text", "").strip():
        parts.append(seg["data"]["text"].strip())
      elif seg["type"] == "image":
        parts.append("[图片]")
      elif seg["type"] == "at":
        parts.append(f"[@{seg['data'].get('qq')}]")
    if parts:
      prefix = f"{nick}({uid})" if include_uid else nick
      lines.append(f"{prefix}: {' '.join(parts)}")
  return lines


@ai_tool(
  description="总结最近的群聊内容，帮不在的人快速了解话题",
  tags=["context"],
  examples=["总结一下刚才聊了什么", "群里在聊啥", "帮我看看最近的话题"],
  triggers=["总结", "摘要"],
  patterns=[r"(聊了|在聊)(什么|啥)"],
  semantic_slots=["聊天总结", "群聊摘要", "话题总结"],
)
async def summarize_chat(ctx: ToolContext, count: int = 30) -> str:
  """总结最近的群聊内容，帮不在的人快速了解话题

  Args:
    count: 获取消息条数(10-50)
  """
  count = max(10, min(50, count))
  try:
    history = await ctx.bot.call_api(
      "get_group_msg_history", group_id=ctx.group_id,
      message_id=str(ctx.event.message_id), count=count,
    )
    messages = history.get("messages", []) if history else []
    if not messages:
      return "暂无聊天记录"

    lines = _parse_qq_messages(messages[-count:])
    if not lines:
      return "最近没有文字消息"

    chat_text = "\n".join(lines[-40:])
    return await llm_complete(
      "用3-5句话总结以下群聊内容的主要话题和要点。简洁直接，不要废话。",
      chat_text,
      temperature=0.3,
      max_tokens=200,
      fallback="无法总结",
    )
  except Exception as e:
    return f"获取聊天记录失败: {e}"


PERIOD_MAP = {"today": "今天", "week": "本周", "month": "本月"}
PERIOD_SECONDS = {"today": 86400, "week": 604800, "month": 2592000}


@ai_tool(
  description="统计群成员发言排行榜",
  tags=["context", "group"],
  examples=["群里谁最活跃", "看看活跃度", "今天谁话最多", "本周发言排行"],
  triggers=["活跃", "话最多"],
  patterns=[r"(谁|哪个).{0,4}(最活跃|话最多)"],
  semantic_slots=["发言排行", "活跃度", "水群排名"],
)
async def group_activity(ctx: ToolContext, period: str = "today") -> str:
  """统计群成员发言排行榜

  Args:
    period: 统计时段(today/week/month)
  """
  if period not in PERIOD_SECONDS:
    period = "today"

  since = time.time() - PERIOD_SECONDS[period]
  label = PERIOD_MAP[period]

  try:
    async with async_session() as session:
      stmt = (
        select(
          MessageStat.nickname,
          func.count().label("cnt"),
        )
        .where(
          MessageStat.group_id == ctx.group_id,
          MessageStat.timestamp >= since,
        )
        .group_by(MessageStat.user_id)
        .order_by(func.count().desc())
        .limit(10)
      )
      result = await session.execute(stmt)
      rows = result.all()

    if not rows:
      return f"{label}暂无发言记录"

    total = sum(r.cnt for r in rows)
    lines = [f"{label}发言排行 (共 {total} 条):"]
    for rank, row in enumerate(rows, 1):
      bar = "█" * (row.cnt * 10 // total) or "▏"
      lines.append(f"{rank}. {row.nickname}: {row.cnt}条 {bar}")

    return "\n".join(lines)
  except Exception as e:
    return f"统计失败: {e}"
