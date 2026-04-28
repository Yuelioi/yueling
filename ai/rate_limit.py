"""AI 调用限流 — 每用户滑动窗口限制"""

import time
from collections import defaultdict


class RateLimiter:
  def __init__(self, max_calls: int = 10, window_seconds: float = 60.0):
    self._max_calls = max_calls
    self._window = window_seconds
    self._calls: dict[str, list[float]] = defaultdict(list)

  def is_allowed(self, user_id: int, group_id: int) -> bool:
    key = f"{group_id}:{user_id}"
    now = time.monotonic()
    timestamps = self._calls[key]

    # 清理过期记录
    self._calls[key] = [t for t in timestamps if now - t < self._window]

    if len(self._calls[key]) >= self._max_calls:
      return False

    self._calls[key].append(now)
    return True

  def remaining(self, user_id: int, group_id: int) -> int:
    key = f"{group_id}:{user_id}"
    now = time.monotonic()
    active = [t for t in self._calls.get(key, []) if now - t < self._window]
    return max(0, self._max_calls - len(active))


rate_limiter = RateLimiter(max_calls=10, window_seconds=60.0)
