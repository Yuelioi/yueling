"""集成测试 — mock LLM 验证全链路 dispatch"""

import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai.confirm import confirm_manager
from ai.dispatcher import dispatch
from ai.rate_limit import rate_limiter
from core.context import ToolContext


# ─── Mock LLM Response 工具 ──────────────────────────────────


def _make_choice(content=None, tool_calls=None):
  choice = MagicMock()
  choice.message.content = content
  choice.message.tool_calls = tool_calls
  choice.message.model_dump.return_value = {
    "role": "assistant",
    "content": content,
    "tool_calls": [
      {
        "id": tc.id,
        "type": "function",
        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
      }
      for tc in (tool_calls or [])
    ] or None,
  }
  return choice


def _make_tool_call(name: str, args: dict, call_id: str = "call_001"):
  tc = MagicMock()
  tc.id = call_id
  tc.function.name = name
  tc.function.arguments = json.dumps(args, ensure_ascii=False)
  return tc


def _make_response(content=None, tool_calls=None):
  resp = MagicMock()
  resp.choices = [_make_choice(content, tool_calls)]
  return resp


@pytest.fixture
def ctx(mock_bot, mock_event):
  return ToolContext(
    user_id=mock_event.user_id,
    group_id=mock_event.group_id,
    role="member",
    bot=mock_bot,
    event=mock_event,
  )


@pytest.fixture
def admin_ctx(mock_bot, mock_event):
  return ToolContext(
    user_id=mock_event.user_id,
    group_id=mock_event.group_id,
    role="admin",
    bot=mock_bot,
    event=mock_event,
  )


@pytest.fixture(autouse=True)
def reset_rate_limiter():
  rate_limiter._calls.clear()
  yield
  rate_limiter._calls.clear()


@pytest.fixture(autouse=True)
def reset_confirm():
  confirm_manager._pending.clear()
  yield
  confirm_manager._pending.clear()


# ─── 正常工具调用 ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dispatch_tool_call_success(ctx):
  """LLM 选择工具 → 执行成功 → 返回结果"""
  from ai.registry import registry, ToolMeta

  async def mock_translate(ctx, text: str, target: str = "en"):
    return f"翻译结果: hello world"

  tool = ToolMeta(
    name="translate",
    description="翻译文本",
    tags=["language"],
    examples=["翻译 hello"],
    parameters={"text": {"type": "string", "description": "原文"}},
    func=mock_translate,
  )

  tc = _make_tool_call("translate", {"text": "你好世界", "target": "en"})
  mock_resp = _make_response(tool_calls=[tc])
  # 第二次调用：LLM 用文本总结（链式终止）
  final_resp = _make_response(content="翻译结果: hello world")
  mock_client = AsyncMock()
  mock_client.chat.completions.create = AsyncMock(side_effect=[mock_resp, final_resp])

  with patch("ai.dispatcher.registry") as mock_reg, \
       patch("ai.executor.registry") as mock_exec_reg, \
       patch("ai.dispatcher.get_llm_client", return_value=mock_client), \
       patch("ai.dispatcher.memory_manager") as mock_mem:
    mock_reg.get_all.return_value = [tool]
    mock_reg.get_by_name.return_value = tool
    mock_exec_reg.get_by_name.return_value = tool
    mock_mem.get_user_context = AsyncMock(return_value="")
    mock_mem.get_group_rules = AsyncMock(return_value=[])
    mock_mem.write_episodic = AsyncMock()

    result = await dispatch("翻译 你好世界", ctx)
    assert "翻译结果" in result


# ─── Guard 拦截 ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_guard_blocks_member_high_risk(ctx):
  """普通成员发送高危指令 → guard 直接拦截，不调用 LLM"""
  from ai.guard import guard_check

  result = guard_check("禁言张三5分钟", "member")
  assert result is not None
  assert "权限不足" in result


@pytest.mark.asyncio
async def test_guard_allows_admin_high_risk():
  """管理员发送高危指令 → guard 放行"""
  from ai.guard import guard_check

  result = guard_check("禁言张三5分钟", "admin")
  assert result is None


# ─── Chat Fallback ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_dispatch_fallback_to_chat(ctx):
  """LLM 不选工具 → fallback 到聊天"""
  from ai.registry import ToolMeta

  tool = ToolMeta(name="translate", description="翻译", tags=["language"])

  mock_resp = _make_response(content="你好呀~")
  mock_client = AsyncMock()
  mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

  with patch("ai.dispatcher.registry") as mock_reg, \
       patch("ai.dispatcher.get_llm_client", return_value=mock_client), \
       patch("ai.dispatcher.memory_manager") as mock_mem, \
       patch("ai.chat.get_llm_client", return_value=mock_client):
    mock_reg.get_all.return_value = [tool]
    mock_mem.get_user_context = AsyncMock(return_value="")
    mock_mem.get_group_rules = AsyncMock(return_value=[])

    # chat_fallback also calls LLM
    chat_resp = _make_response(content="哈喽~ [评分：+3]")
    mock_client.chat.completions.create = AsyncMock(return_value=chat_resp)

    result = await dispatch("你好", ctx)
    assert result is not None


# ─── 确认流程 ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dispatch_confirm_flow(admin_ctx):
  """高危工具触发确认 → 返回确认码"""
  from ai.registry import ToolMeta

  async def mock_ban(ctx, user: int, duration: int = 1):
    return f"已禁言 {duration} 分钟"

  tool = ToolMeta(
    name="ban_user",
    description="禁言",
    tags=["moderation", "group"],
    parameters={"user": {"type": "integer"}, "duration": {"type": "integer"}},
    permission="admin",
    risk_level="high",
    confirm_required=True,
    func=mock_ban,
  )

  tc = _make_tool_call("ban_user", {"user": 12345, "duration": 5})
  mock_resp = _make_response(tool_calls=[tc])
  mock_client = AsyncMock()
  mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

  with patch("ai.dispatcher.registry") as mock_reg, \
       patch("ai.dispatcher.get_llm_client", return_value=mock_client), \
       patch("ai.dispatcher.memory_manager") as mock_mem:
    mock_reg.get_all.return_value = [tool]
    mock_reg.get_by_name.return_value = tool
    mock_mem.get_user_context = AsyncMock(return_value="")
    mock_mem.get_group_rules = AsyncMock(return_value=[])

    result = await dispatch("禁言12345五分钟", admin_ctx)
    assert "确认" in result
    assert "30秒" in result


# ─── 重试逻辑 ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dispatch_retry_on_error(ctx):
  """第一次执行失败 → ERROR 回注 → LLM 重新选择 → 成功"""
  from ai.registry import ToolMeta

  call_count = 0

  async def mock_calc(ctx, expression: str):
    nonlocal call_count
    call_count += 1
    if call_count == 1:
      return "ERROR:表达式无效"
    return "结果: 42"

  tool = ToolMeta(
    name="calculate",
    description="计算",
    tags=["math"],
    parameters={"expression": {"type": "string"}},
    func=mock_calc,
  )

  tc1 = _make_tool_call("calculate", {"expression": "invalid"}, "call_001")
  resp1 = _make_response(tool_calls=[tc1])
  tc2 = _make_tool_call("calculate", {"expression": "6*7"}, "call_002")
  resp2 = _make_response(tool_calls=[tc2])
  # 第三次调用：链式终止，文本总结
  resp3 = _make_response(content="结果: 42")

  mock_client = AsyncMock()
  mock_client.chat.completions.create = AsyncMock(side_effect=[resp1, resp2, resp3])

  with patch("ai.dispatcher.registry") as mock_reg, \
       patch("ai.executor.registry") as mock_exec_reg, \
       patch("ai.dispatcher.get_llm_client", return_value=mock_client), \
       patch("ai.dispatcher.memory_manager") as mock_mem:
    mock_reg.get_all.return_value = [tool]
    mock_reg.get_by_name.return_value = tool
    mock_exec_reg.get_by_name.return_value = tool
    mock_mem.get_user_context = AsyncMock(return_value="")
    mock_mem.get_group_rules = AsyncMock(return_value=[])
    mock_mem.write_episodic = AsyncMock()

    result = await dispatch("计算 6*7", ctx)
    assert "42" in result
    assert call_count == 2


# ─── Rate Limit ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dispatch_rate_limited(ctx):
  """超过速率限制 → 返回提示"""
  for _ in range(10):
    rate_limiter.is_allowed(ctx.user_id, ctx.group_id)

  result = await dispatch("翻译 hello", ctx)
  assert "太快" in result


# ─── Memory 写入 ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dispatch_writes_semantic_memory(ctx):
  """输入匹配触发词 → 写入语义记忆"""
  from ai.registry import ToolMeta

  tool = ToolMeta(name="t", description="test", tags=["fun"])
  mock_resp = _make_response(content="好的~")
  mock_client = AsyncMock()
  mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

  with patch("ai.dispatcher.registry") as mock_reg, \
       patch("ai.dispatcher.get_llm_client", return_value=mock_client), \
       patch("ai.dispatcher.memory_manager") as mock_mem, \
       patch("ai.chat.get_llm_client", return_value=mock_client):
    mock_reg.get_all.return_value = [tool]
    mock_mem.get_user_context = AsyncMock(return_value="")
    mock_mem.get_group_rules = AsyncMock(return_value=[])
    mock_mem.write_semantic = AsyncMock()
    mock_mem.smart_write_semantic = AsyncMock()

    chat_resp = _make_response(content="知道了~ [评分：+2]")
    mock_client.chat.completions.create = AsyncMock(return_value=chat_resp)

    await dispatch("我喜欢碧蓝档案", ctx)
    mock_mem.smart_write_semantic.assert_called_once()
    call_args = mock_mem.smart_write_semantic.call_args
    assert "碧蓝档案" in str(call_args)


# ─── Group Rules 注入 ────────────────────────────────────────


@pytest.mark.asyncio
async def test_dispatch_injects_group_rules(ctx):
  """群有自定义规则 → system message 中包含规则"""
  from ai.registry import ToolMeta

  tool = ToolMeta(name="t", description="test", tags=["fun"])

  async def mock_translate(ctx, text: str):
    return "ok"

  tool.func = mock_translate
  tc = _make_tool_call("t", {"text": "hi"})
  mock_resp = _make_response(tool_calls=[tc])
  mock_client = AsyncMock()
  mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

  with patch("ai.dispatcher.registry") as mock_reg, \
       patch("ai.executor.registry") as mock_exec_reg, \
       patch("ai.dispatcher.get_llm_client", return_value=mock_client), \
       patch("ai.dispatcher.memory_manager") as mock_mem:
    mock_reg.get_all.return_value = [tool]
    mock_reg.get_by_name.return_value = tool
    mock_exec_reg.get_by_name.return_value = tool
    mock_mem.get_user_context = AsyncMock(return_value="")
    mock_mem.get_group_rules = AsyncMock(return_value=["本群禁止讨论政治", "回复要用中文"])
    mock_mem.write_semantic = AsyncMock()
    mock_mem.write_episodic = AsyncMock()

    await dispatch("你好", ctx)

    create_call = mock_client.chat.completions.create.call_args
    messages = create_call.kwargs.get("messages") or create_call[1].get("messages", [])
    system_text = messages[0]["content"] if messages else ""
    assert "本群禁止讨论政治" in system_text


# ─── Proactive 不干扰 ai_dispatch ────────────────────────────


def test_proactive_respects_cooldown():
  """主动发言遵守冷却时间"""
  from ai.proactive import proactive_manager

  proactive_manager.record_speak(200001)
  proactive_manager.feed_message(200001, 100001, "月灵你好")
  proactive_manager.feed_message(200001, 100002, "月灵在吗")
  proactive_manager.feed_message(200001, 100003, "月灵帮忙")

  assert not proactive_manager.should_speak(200001)
