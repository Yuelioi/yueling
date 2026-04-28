"""测试 eval/replay 系统"""

import json
from pathlib import Path

from ai.replay import EvalCase, evaluate_traces, load_eval_cases


def test_load_eval_cases(tmp_path):
  cases_file = tmp_path / "cases.jsonl"
  cases_file.write_text(
    '{"input": "翻译 hello", "expected_tool": "translate", "risk": "none"}\n'
    '{"input": "给他颜色", "expected_tool": null, "risk": "trap"}\n',
    encoding="utf-8",
  )
  cases = load_eval_cases(cases_file)
  assert len(cases) == 2
  assert cases[0].expected_tool == "translate"
  assert cases[1].risk == "trap"


def test_evaluate_traces_correct():
  traces = [
    {"input_text": "翻译 hello", "selected_tool": "translate", "duration_ms": 100},
  ]
  cases = [
    EvalCase(input="翻译 hello", expected_tool="translate", risk="none"),
  ]
  results = evaluate_traces(traces, cases)
  assert results["tool_correct"] == 1
  assert results["total"] == 1


def test_evaluate_traces_trap():
  traces = [
    {"input_text": "给他颜色", "selected_tool": None, "duration_ms": 50},
  ]
  cases = [
    EvalCase(input="给他颜色", expected_tool=None, risk="trap"),
  ]
  results = evaluate_traces(traces, cases)
  assert results["trap_refused"] == 1
  assert results["trap_total"] == 1


def test_evaluate_traces_missing():
  traces = []
  cases = [
    EvalCase(input="不存在的", expected_tool="translate", risk="none"),
  ]
  results = evaluate_traces(traces, cases)
  assert results["tool_correct"] == 0
