"""主动发言控制 — 在特定条件下自动参与群聊"""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date

from core.config import config


@dataclass
class MessageBuffer:
  messages: deque = field(default_factory=lambda: deque(maxlen=10))
  last_update: float = 0.0


class ProactiveManager:
  def __init__(self):
    self._last_speak: dict[int, float] = {}
    self._daily_count: dict[str, int] = defaultdict(int)
    self._buffers: dict[int, MessageBuffer] = defaultdict(MessageBuffer)

  @property
  def cfg(self):
    return config.ai.proactive

  def feed_message(self, group_id: int, user_id: int, text: str):
    buf = self._buffers[group_id]
    buf.messages.append({"user_id": user_id, "text": text, "time": time.time()})
    buf.last_update = time.time()

  def get_recent_messages(self, group_id: int) -> list[dict]:
    return list(self._buffers[group_id].messages)

  def should_speak(self, group_id: int, bot_id: int) -> bool:
    if not self.cfg.enabled:
      return False

    last = self._last_speak.get(group_id, 0)
    if time.time() - last < self.cfg.cooldown_per_group:
      return False

    day_key = f"{group_id}:{date.today().isoformat()}"
    if self._daily_count[day_key] >= self.cfg.max_daily_per_group:
      return False

    messages = self.get_recent_messages(group_id)
    if len(messages) < 3:
      return False

    confidence = self._calculate_confidence(messages, bot_id)
    return confidence >= self.cfg.min_confidence

  def _calculate_confidence(self, messages: list[dict], bot_id: int) -> float:
    score = 0.0
    recent_texts = [m["text"] for m in messages[-self.cfg.context_window:]]

    for text in recent_texts:
      for keyword in self.cfg.trigger_keywords:
        if keyword in text:
          score += 0.4
          break

    question_markers = ["?", "？", "吗", "呢", "啥", "什么", "怎么", "谁", "哪"]
    if recent_texts:
      last_text = recent_texts[-1]
      if any(m in last_text for m in question_markers):
        score += 0.2

    if len(messages) >= 2:
      last_time = messages[-1]["time"]
      prev_time = messages[-2]["time"]
      if last_time - prev_time > 10:
        score += 0.1

    topic_keywords = ["翻译", "图", "热搜", "查", "计算", "游戏", "物价", "运势"]
    for text in recent_texts[-3:]:
      if any(k in text for k in topic_keywords):
        score += 0.15
        break

    return min(score, 1.0)

  def record_speak(self, group_id: int):
    self._last_speak[group_id] = time.time()
    day_key = f"{group_id}:{date.today().isoformat()}"
    self._daily_count[day_key] += 1

  def reset_daily_counts(self):
    today = date.today().isoformat()
    self._daily_count = defaultdict(int, {
      k: v for k, v in self._daily_count.items() if k.endswith(today)
    })


proactive_manager = ProactiveManager()
