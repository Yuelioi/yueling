"""验证 ToolTrace 新字段和 record_trace 兼容性"""

import json
from pathlib import Path

from ai.trace import TRACE_FILE, ToolTrace, record_trace, start_trace


def test_tool_trace_has_new_fields():
  t = ToolTrace()
  assert t.recall_sources == {}
  assert t.candidates_ranked == []
  assert t.result_status == "ok"
  assert t.route_latency_ms == 0
  assert t.llm_latency_ms == 0


def test_record_trace_legacy_signature_still_works():
  start_trace()
  record_trace("hello", "tool_a", {"x": 1}, "result", 1)
  # 不报错就算通过，文件应能写入
  assert TRACE_FILE.exists()


def test_record_trace_with_new_fields():
  start_trace()
  record_trace(
    input_text="测试输入",
    tool_name="my_tool",
    tool_args={"x": 1},
    result="ok",
    steps=2,
    recall_sources={"my_tool": "R1", "other": "R3"},
    candidates_ranked=[("my_tool", 1.0), ("other", 0.65)],
    result_status="ok",
    route_latency_ms=12.3,
    llm_latency_ms=820.5,
  )
  with open(TRACE_FILE, encoding="utf-8") as f:
    last = f.readlines()[-1]
  data = json.loads(last)
  assert data["input_text"] == "测试输入"
  assert data["recall_sources"]["my_tool"] == "R1"
  assert data["candidates_ranked"][0] == ["my_tool", 1.0]
  assert data["result_status"] == "ok"
  assert data["route_latency_ms"] == 12.3
