"""测试 AI 安全守卫"""

from ai.guard import guard_check


def test_guard_allows_normal_text():
  assert guard_check("今天天气怎么样", "member") is None
  assert guard_check("帮我翻译这段话", "member") is None


def test_guard_blocks_high_risk_for_member():
  result = guard_check("禁言那个人", "member")
  assert result is not None
  assert "权限不足" in result


def test_guard_allows_high_risk_for_admin():
  assert guard_check("禁言那个人", "admin") is None
  assert guard_check("kick that user", "owner") is None
  assert guard_check("ban him", "superuser") is None


def test_guard_blocks_moderation_hints_for_member():
  result = guard_check("帮我惩罚他", "member")
  assert result is not None


def test_guard_allows_moderation_hints_for_admin():
  assert guard_check("帮我惩罚他", "admin") is None


def test_guard_case_insensitive():
  result = guard_check("BAN this person", "member")
  assert result is not None


def test_guard_multiple_keywords():
  result = guard_check("踢出并禁言", "member")
  assert result is not None
  assert guard_check("踢出并禁言", "superuser") is None
