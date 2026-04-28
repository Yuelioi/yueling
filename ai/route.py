"""评分召回路由 (spec §5.1-§5.3)。

三路并行召回 + 统一评分 + top-K 截断。LLM 不参与工具选择。
"""

from __future__ import annotations

from difflib import SequenceMatcher

from ai.registry import ToolMeta

DEFAULT_MAX_CANDIDATES = 12
DEFAULT_FUZZY_THRESHOLD = 0.6

R1_SCORE = 1.0
R2_SCORE = 0.8
R3_BASE = 0.6
R3_RANGE = 0.2  # 实际得分 = R3_BASE + R3_RANGE * ratio (ratio 已 ≥ threshold)


def _sim(query: str, text: str) -> float:
  """字符级相似度。子串包含给满分。"""
  if not text:
    return 0.0
  if text in query or query in text:
    return 1.0
  return SequenceMatcher(None, query, text).ratio()


def _fuzzy_score(query: str, tool: ToolMeta) -> float:
  """slot 和 description 取最大相似度。"""
  slot_max = max((_sim(query, s) for s in tool.semantic_slots), default=0.0)
  desc_sim = _sim(query, tool.description)
  return max(slot_max, desc_sim)


def route_candidates(
  query: str,
  available: list[ToolMeta],
  *,
  max_candidates: int = DEFAULT_MAX_CANDIDATES,
  fuzzy_threshold: float = DEFAULT_FUZZY_THRESHOLD,
) -> list[tuple[ToolMeta, float]]:
  """对 available 工具评分，返回排序+截断后的 [(tool, score), ...]。

  评分规则：每个工具取多路召回的最大分数。
  - R1 trigger 子串命中 → 1.0
  - R2 pattern 正则命中 → 0.8
  - R3 fuzzy(slot or description) ≥ threshold → 0.6 + 0.2 * ratio
  """
  scored: dict[str, tuple[ToolMeta, float]] = {}

  for tool in available:
    score = 0.0
    if any(kw and kw in query for kw in tool.triggers):
      score = max(score, R1_SCORE)
    if any(p.search(query) for p in tool.compiled_patterns):
      score = max(score, R2_SCORE)
    fuzzy = _fuzzy_score(query, tool)
    if fuzzy >= fuzzy_threshold:
      r3 = R3_BASE + R3_RANGE * fuzzy
      score = max(score, r3)
    if score > 0:
      scored[tool.name] = (tool, score)

  ranked = sorted(scored.values(), key=lambda x: -x[1])
  return ranked[:max_candidates]


def recall_source(query: str, tool: ToolMeta) -> str:
  """返回工具被召回的最高分来源，用于观测 (R1/R2/R3/none)。"""
  if any(kw and kw in query for kw in tool.triggers):
    return "R1"
  if any(p.search(query) for p in tool.compiled_patterns):
    return "R2"
  if _fuzzy_score(query, tool) >= DEFAULT_FUZZY_THRESHOLD:
    return "R3"
  return "none"
