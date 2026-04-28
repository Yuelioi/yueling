"""AI 调度链路追踪 — 记录每次调用的完整日志"""

import contextvars
import json
import time
from dataclasses import asdict, dataclass, field

from core.config import config

TRACE_DIR = config.paths.data / "ai_traces"
TRACE_DIR.mkdir(parents=True, exist_ok=True)
TRACE_FILE = TRACE_DIR / "traces.jsonl"


@dataclass
class ToolTrace:
  timestamp: float = field(default_factory=time.time)
  input_text: str = ""
  selected_tool: str | None = None
  tool_args: dict = field(default_factory=dict)
  result: str = ""
  total_steps: int = 0
  duration_ms: float = 0
  # v3 新增 (本任务)
  recall_sources: dict[str, str] = field(default_factory=dict)
  candidates_ranked: list[tuple[str, float]] = field(default_factory=list)
  result_status: str = "ok"  # ok / error / fallback / clarify
  route_latency_ms: float = 0
  llm_latency_ms: float = 0


_trace_start: contextvars.ContextVar[float] = contextvars.ContextVar("_trace_start", default=0.0)


def start_trace():
  _trace_start.set(time.time())


def record_trace(
  input_text: str,
  tool_name: str | None,
  tool_args: dict,
  result: str,
  steps: int,
  *,
  recall_sources: dict[str, str] | None = None,
  candidates_ranked: list[tuple[str, float]] | None = None,
  result_status: str = "ok",
  route_latency_ms: float = 0,
  llm_latency_ms: float = 0,
):
  start = _trace_start.get()
  duration = (time.time() - start) * 1000 if start else 0

  trace = ToolTrace(
    input_text=input_text,
    selected_tool=tool_name,
    tool_args=tool_args,
    result=result[:200],
    total_steps=steps,
    duration_ms=round(duration, 1),
    recall_sources=recall_sources or {},
    candidates_ranked=candidates_ranked or [],
    result_status=result_status,
    route_latency_ms=round(route_latency_ms, 1),
    llm_latency_ms=round(llm_latency_ms, 1),
  )

  try:
    with open(TRACE_FILE, "a", encoding="utf-8") as f:
      f.write(json.dumps(asdict(trace), ensure_ascii=False) + "\n")
  except Exception:
    pass
