"""主动发言控制 — 整数积分制，积满触发，拿上下文走 AI 回复"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date

from core.config import config


@dataclass
class GroupHeat:
  score: int = 0
  messages: deque = field(default_factory=lambda: deque(maxlen=20))
  last_msg_time: float = 0.0
  last_speak_time: float = 0.0
  normal_streak: int = 0  # 连续非特殊发言计数
  daily_count: int = 0
  daily_date: str = ""

  def reset_daily_if_needed(self):
    today = date.today().isoformat()
    if self.daily_date != today:
      self.daily_count = 0
      self.daily_date = today


# ─── 积分规则 ──────────────────────────────────────────────

SCORE_PER_MESSAGE = 2
SCORE_MENTION_BOT = 15
SCORE_QUESTION = 5
SCORE_TOPIC_KEYWORD = 3
SCORE_LONG_GAP = 8
SCORE_THRESHOLD = 100
MIN_NORMAL_STREAK = 3

TOPIC_KEYWORDS = [
  "月灵", "翻译", "图", "热搜", "查", "计算", "游戏", "物价",
  "运势", "天气", "搜", "帮我", "谁", "什么", "怎么",
]
QUESTION_MARKERS = ["?", "？", "吗", "呢", "啥", "什么", "怎么", "谁", "哪", "吧"]


class ProactiveManager:
  def __init__(self):
    self._heats: dict[int, GroupHeat] = defaultdict(GroupHeat)

  @property
  def cfg(self):
    return config.ai.proactive

  def _get(self, group_id: int) -> GroupHeat:
    return self._heats[group_id]

  def feed_message(self, group_id: int, user_id: int, text: str):
    """每条普通群消息调用（非@bot），累积积分"""
    h = self._get(group_id)
    h.reset_daily_if_needed()
    now = time.time()

    h.messages.append({"user_id": user_id, "text": text, "time": now})
    h.normal_streak += 1
    h.score += SCORE_PER_MESSAGE

    if any(k in text for k in ["月灵"]):
      h.score += SCORE_MENTION_BOT

    if any(m in text for m in QUESTION_MARKERS):
      h.score += SCORE_QUESTION

    if any(k in text for k in TOPIC_KEYWORDS):
      h.score += SCORE_TOPIC_KEYWORD

    if h.last_msg_time and (now - h.last_msg_time) > 30:
      h.score += SCORE_LONG_GAP

    h.last_msg_time = now

  def on_bot_replied(self, group_id: int):
    """AI 调度回复了（@bot 或主动发言后），重置积分和连续计数"""
    h = self._get(group_id)
    h.score = 0
    h.normal_streak = 0

  def should_speak(self, group_id: int) -> bool:
    if not self.cfg.enabled:
      return False

    h = self._get(group_id)
    h.reset_daily_if_needed()

    if h.daily_count >= self.cfg.max_daily_per_group:
      return False

    if h.last_speak_time and (time.time() - h.last_speak_time) < self.cfg.cooldown_per_group:
      return False

    if h.normal_streak < MIN_NORMAL_STREAK:
      return False

    return h.score >= SCORE_THRESHOLD

  def record_speak(self, group_id: int):
    h = self._get(group_id)
    h.score = 0
    h.normal_streak = 0
    h.last_speak_time = time.time()
    h.daily_count += 1

  def get_recent_context(self, group_id: int) -> str:
    """获取最近消息作为上下文"""
    h = self._get(group_id)
    if not h.messages:
      return ""
    lines = []
    for msg in list(h.messages)[-10:]:
      lines.append(msg["text"])
    return "\n".join(lines)

  def reset_daily_counts(self):
    for h in self._heats.values():
      h.reset_daily_if_needed()


proactive_manager = ProactiveManager()
