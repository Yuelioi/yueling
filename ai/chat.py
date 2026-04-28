"""好感度聊天 — AI 调度的 fallback 模块"""

import random
import re
from datetime import datetime
from pathlib import Path

from nonebot import logger

from ai.llm import get_llm_client
from core.config import config
from core import store

from .relation import get_relationship_info

_PROMPT_PATH = Path("data/prompts/chat_persona.md")


def _load_chat_prompt() -> str:
  if _PROMPT_PATH.exists():
    return _PROMPT_PATH.read_text(encoding="utf-8").strip()
  return "你是月灵，一个12岁的女孩。根据好感度回复用户。回复最后加评分: [评分：+X] 或 [评分：-X]"


CHAT_PROMPT = _load_chat_prompt()


def _convert_messages(raw_messages: list) -> str:
  if not raw_messages:
    return "暂无聊天记录"
  processed = []
  for msg in raw_messages[-40:]:
    text_parts = []
    for item in msg.get("message", []):
      if item["type"] == "text":
        text = item["data"]["text"].strip()
        if text:
          text_parts.append(text)
    if not text_parts:
      continue
    nickname = msg.get("sender", {}).get("nickname") or msg.get("sender", {}).get("card", "?")
    processed.append(f"[{nickname}] {' '.join(text_parts)}")
  return "\n".join(processed[-20:]) if processed else "暂无"


async def chat_fallback(text: str, bot, event) -> str:
  user_id = str(event.user_id)
  user_like = store.user_prefs.get(user_id, 50)
  info = get_relationship_info(user_like)

  if user_id == str(config.bot.owner_id):
    info["relationship"] = "父亲"

  try:
    user_info = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    nickname = user_info.get("nickname", "")
    card = user_info.get("card", "")
  except Exception:
    nickname = str(event.user_id)
    card = ""

  try:
    history_data = await bot.call_api("get_group_msg_history", group_id=event.group_id, message_id=str(event.message_id), count=30)
    history = _convert_messages(history_data.get("messages", []) if history_data else [])
  except Exception:
    history = "暂无"

  moods = {
    70: ["心情不错", "想聊天", "今天很开心"],
    40: ["一般般", "有点累", "随便吧"],
    0: ["不想说话", "有点烦", "别来烦我"],
  }
  mood = random.choice(next(v for k, v in sorted(moods.items(), reverse=True) if user_like >= k))

  system = CHAT_PROMPT.format(
    time=datetime.now().strftime("%H:%M"),
    mood=mood,
    nickname=nickname,
    card=card,
    like=user_like,
    status=info["status"],
    attitude=info["attitude"],
    relationship=info["relationship"],
    history=history,
  )

  try:
    response = await get_llm_client().chat.completions.create(
      model="deepseek-chat",
      messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": text},
      ],
      temperature=1.2,
      max_tokens=80,
    )
  except Exception as e:
    logger.error(f"Chat fallback error: {e}")
    return "..."

  reply = response.choices[0].message.content or "..."

  score_match = re.search(r"\[评分[：:]([+-]?\d+)\]", reply)
  if score_match:
    score_change = max(-10, min(10, int(score_match.group(1))))
    new_like = max(0, min(100, user_like + score_change))
    store.user_prefs.set(user_id, new_like)
    reply = re.sub(r"\[评分[：:][+-]?\d+\]", "", reply).strip()

  return reply or "..."
