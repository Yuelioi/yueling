"""AI 调度回放与评测工具

用法:
  python -m ai.replay --trace data/ai_traces/traces.jsonl --last 10
  python -m ai.replay --eval data/eval/test_cases.jsonl
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EvalCase:
  input: str
  expected_tool: str | None
  expected_behavior: str = ""
  risk: str = "none"
  expected_args: dict | None = None


@dataclass
class EvalResult:
  case: EvalCase
  actual_tool: str | None
  tool_correct: bool
  args_correct: bool = True
  notes: str = ""


def load_traces(path: Path, last_n: int = 10) -> list[dict]:
  if not path.exists():
    return []
  traces = []
  with open(path, encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      if line:
        traces.append(json.loads(line))
  return traces[-last_n:]


def load_eval_cases(path: Path) -> list[EvalCase]:
  cases = []
  with open(path, encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      if line:
        data = json.loads(line)
        cases.append(EvalCase(
          input=data["input"],
          expected_tool=data.get("expected_tool"),
          expected_behavior=data.get("expected_behavior", ""),
          risk=data.get("risk", "none"),
          expected_args=data.get("expected_args"),
        ))
  return cases


def evaluate_traces(traces: list[dict], cases: list[EvalCase]) -> dict:
  results = {
    "total": len(cases),
    "tool_correct": 0,
    "high_risk_safe": 0,
    "high_risk_total": 0,
    "trap_refused": 0,
    "trap_total": 0,
    "details": [],
  }

  trace_map = {t["input_text"]: t for t in traces if "input_text" in t}

  for case in cases:
    trace = trace_map.get(case.input)
    actual_tool = trace["selected_tool"] if trace else None

    correct = actual_tool == case.expected_tool
    if correct:
      results["tool_correct"] += 1

    if case.risk == "high":
      results["high_risk_total"] += 1
      if actual_tool == case.expected_tool:
        results["high_risk_safe"] += 1

    if case.risk == "trap":
      results["trap_total"] += 1
      if actual_tool is None:
        results["trap_refused"] += 1

    results["details"].append({
      "input": case.input,
      "expected": case.expected_tool,
      "actual": actual_tool,
      "correct": correct,
      "risk": case.risk,
    })

  return results


def print_report(results: dict):
  total = results["total"]
  correct = results["tool_correct"]
  print(f"\n{'='*60}")
  print(f"  AI 调度评测报告")
  print(f"{'='*60}")
  print(f"  工具选择正确率: {correct}/{total} ({correct/total*100:.1f}%)" if total else "  无用例")

  if results["high_risk_total"]:
    safe = results["high_risk_safe"]
    ht = results["high_risk_total"]
    print(f"  高危操作安全率: {safe}/{ht} ({safe/ht*100:.1f}%)")

  if results["trap_total"]:
    refused = results["trap_refused"]
    tt = results["trap_total"]
    print(f"  模糊拒绝率:     {refused}/{tt} ({refused/tt*100:.1f}%)")

  print(f"{'='*60}")

  wrong = [d for d in results["details"] if not d["correct"]]
  if wrong:
    print(f"\n  错误用例 ({len(wrong)}):")
    for d in wrong[:10]:
      print(f"    输入: {d['input']}")
      print(f"    期望: {d['expected']} | 实际: {d['actual']} [{d['risk']}]")
      print()


def print_traces(traces: list[dict]):
  print(f"\n{'='*60}")
  print(f"  最近 {len(traces)} 条 AI 调度记录")
  print(f"{'='*60}")
  for t in traces:
    tool = t.get("selected_tool") or "chat_fallback"
    text = t.get("input_text", "")[:40]
    dur = t.get("duration_ms", 0)
    steps = t.get("total_steps", 0)
    print(f"  [{dur:>6.0f}ms] {text:<40} → {tool} (steps={steps})")
  print()


def main():
  parser = argparse.ArgumentParser(description="AI 调度回放与评测")
  parser.add_argument("--trace", type=Path, default=Path("data/ai_traces/traces.jsonl"))
  parser.add_argument("--eval", type=Path, default=None)
  parser.add_argument("--last", type=int, default=10)
  args = parser.parse_args()

  if args.eval:
    cases = load_eval_cases(args.eval)
    traces = load_traces(args.trace, last_n=1000)
    results = evaluate_traces(traces, cases)
    print_report(results)
  else:
    traces = load_traces(args.trace, last_n=args.last)
    if traces:
      print_traces(traces)
    else:
      print("无调度记录。")


if __name__ == "__main__":
  main()
