"""测试 AI dispatcher 中的工具选择逻辑"""

from ai.dispatcher import get_available_tools, select_candidate_tools, INTENT_TAG_MAP
from ai.registry import ToolMeta, ToolRegistry


def _make_tool(name: str, tags: list[str], permission: str = "member") -> ToolMeta:
  return ToolMeta(name=name, description=f"Tool {name}", tags=tags, permission=permission)


def test_get_available_tools_filters_admin():
  from unittest.mock import patch

  tools = [
    _make_tool("public", ["fun"]),
    _make_tool("admin_tool", ["mod"], permission="admin"),
    _make_tool("super_tool", ["sys"], permission="superuser"),
  ]

  with patch("ai.dispatcher.registry") as mock_reg:
    mock_reg.get_all.return_value = tools

    member_tools = get_available_tools("member")
    assert len(member_tools) == 1
    assert member_tools[0].name == "public"

    admin_tools = get_available_tools("admin")
    assert len(admin_tools) == 2

    super_tools = get_available_tools("superuser")
    assert len(super_tools) == 3


def test_select_candidate_tools_by_keyword():
  tools = [
    _make_tool("translate", ["language"]),
    _make_tool("roll", ["fun", "random"]),
    _make_tool("ban_user", ["moderation", "group"]),
  ]

  result = select_candidate_tools("帮我翻译这句话", tools)
  assert any(t.name == "translate" for t in result)

  result = select_candidate_tools("roll一下", tools)
  assert any(t.name == "roll" for t in result)


def test_select_candidate_tools_no_match_returns_all():
  tools = [
    _make_tool("a", ["x"]),
    _make_tool("b", ["y"]),
  ]
  result = select_candidate_tools("完全不匹配的文字", tools)
  assert len(result) == 2


def test_select_candidate_tools_respects_max():
  tools = [_make_tool(f"tool_{i}", ["fun"]) for i in range(20)]
  result = select_candidate_tools("随机", tools, step=0)
  assert len(result) <= 10

  result = select_candidate_tools("随机", tools, step=1)
  assert len(result) <= 10
