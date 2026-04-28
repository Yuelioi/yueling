"""测试 AI 限流"""

import time
from unittest.mock import patch

from ai.rate_limit import RateLimiter


def test_allows_within_limit():
  limiter = RateLimiter(max_calls=3, window_seconds=60.0)
  assert limiter.is_allowed(100, 200) is True
  assert limiter.is_allowed(100, 200) is True
  assert limiter.is_allowed(100, 200) is True


def test_blocks_over_limit():
  limiter = RateLimiter(max_calls=2, window_seconds=60.0)
  assert limiter.is_allowed(100, 200) is True
  assert limiter.is_allowed(100, 200) is True
  assert limiter.is_allowed(100, 200) is False


def test_different_users_independent():
  limiter = RateLimiter(max_calls=1, window_seconds=60.0)
  assert limiter.is_allowed(100, 200) is True
  assert limiter.is_allowed(101, 200) is True
  assert limiter.is_allowed(100, 200) is False


def test_window_expiry():
  limiter = RateLimiter(max_calls=1, window_seconds=0.1)
  assert limiter.is_allowed(100, 200) is True
  assert limiter.is_allowed(100, 200) is False
  time.sleep(0.15)
  assert limiter.is_allowed(100, 200) is True


def test_remaining():
  limiter = RateLimiter(max_calls=5, window_seconds=60.0)
  assert limiter.remaining(100, 200) == 5
  limiter.is_allowed(100, 200)
  limiter.is_allowed(100, 200)
  assert limiter.remaining(100, 200) == 3
