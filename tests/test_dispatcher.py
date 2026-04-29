"""测试 AI dispatcher 中的工具选择逻辑"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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
  assert len(result) <= 15

  result = select_candidate_tools("随机", tools, step=1)
  assert len(result) <= 15


@pytest.mark.asyncio
async def test_dispatch_fallback_writes_trace_fields(tmp_path):
  """dispatch() fallback 路径写 trace 时包含 v3 新字段"""
  trace_file = tmp_path / "traces.jsonl"

  mock_choice = MagicMock()
  mock_choice.message.tool_calls = None
  mock_choice.message.content = "聊天回复"

  mock_response = MagicMock()
  mock_response.choices = [mock_choice]

  mock_llm = AsyncMock()
  mock_llm.chat.completions.create = AsyncMock(return_value=mock_response)

  mock_session = MagicMock()
  mock_session.step_count = 0
  mock_session.last_meaningful_input = ""
  mock_session.get_compressed_context = AsyncMock(return_value=[])

  mock_ctx = MagicMock()
  mock_ctx.user_id = 123
  mock_ctx.group_id = 456
  mock_ctx.role = "member"
  mock_ctx.get_images.return_value = []
  mock_ctx.bot = AsyncMock()
  mock_ctx.event = MagicMock()

  test_tool = ToolMeta(
    name="test_tool", description="test", tags=["fun"],
    triggers=["测试"], semantic_slots=["test"],
  )

  with (
    patch("ai.dispatcher.rate_limiter") as mock_rl,
    patch("ai.dispatcher.registry") as mock_reg,
    patch("ai.dispatcher.get_llm_client", return_value=mock_llm),
    patch("ai.dispatcher.session_manager") as mock_sm,
    patch("ai.dispatcher.confirm_manager") as mock_cm,
    patch("ai.dispatcher.memory_manager") as mock_mm,
    patch("ai.dispatcher.build_system_message", return_value="system"),
    patch("ai.trace.TRACE_FILE", trace_file),
    patch("ai.chat.chat_fallback", new_callable=AsyncMock, return_value="fallback reply"),
    patch("ai.dispatcher.should_write_semantic", return_value=False),
  ):
    mock_rl.is_allowed.return_value = True
    mock_reg.get_all.return_value = [test_tool]
    mock_sm.get.return_value = mock_session
    mock_cm.try_confirm.return_value = None
    mock_mm.get_group_rules = AsyncMock(return_value=[])
    mock_mm.get_user_context = AsyncMock(return_value="")

    from ai.dispatcher import dispatch
    result = await dispatch("你好呀", mock_ctx)

  assert trace_file.exists()
  last_line = trace_file.read_text().strip().split("\n")[-1]
  data = json.loads(last_line)

  assert "recall_sources" in data
  assert "candidates_ranked" in data
  assert "result_status" in data
  assert data["result_status"] == "fallback"
  assert "route_latency_ms" in data
  assert "llm_latency_ms" in data
  assert "tool_latency_ms" in data
