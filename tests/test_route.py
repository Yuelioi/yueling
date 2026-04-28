"""验证评分召回路由 (spec §5.1-§5.3)"""

import re

from ai.registry import ToolMeta
from ai.route import route_candidates


def _make(name, triggers=None, patterns=None, slots=None, desc=""):
  return ToolMeta(
    name=name,
    description=desc,
    triggers=triggers or [],
    patterns=patterns or [],
    semantic_slots=slots or [],
  )


def test_r1_trigger_hit_gives_score_1():
  tools = [_make("translate", triggers=["翻译"])]
  result = route_candidates("帮我翻译这段", tools)
  assert len(result) == 1
  assert result[0][0].name == "translate"
  assert result[0][1] == 1.0


def test_r2_pattern_hit_gives_score_0_8():
  tools = [_make("translate", patterns=[r"把.*翻译成"])]
  result = route_candidates("把这段翻译成英文", tools)
  assert result[0][1] == 0.8


def test_r3_only_when_above_threshold():
  tools = [_make("translate", slots=["翻译"], desc="翻译文本")]
  # 完全无关查询：不应进入候选
  result = route_candidates("xyzasdf", tools)
  assert result == []


def test_r3_fuzzy_against_description():
  # slot 是"完全无关的词"，但 query 跟 description 更像
  tools = [_make("translate", slots=["完全无关的词"], desc="翻译文本到目标语言")]
  result = route_candidates("翻译文本", tools)
  assert len(result) == 1


def test_max_score_when_multiple_paths_hit():
  tools = [_make("translate", triggers=["翻译"], slots=["翻译"])]
  result = route_candidates("翻译这段", tools)
  # R1 (1.0) 和 R3 (1.0 因子串包含) 都命中，取最大
  assert result[0][1] == 1.0


def test_ranking_orders_by_score_desc():
  tools = [
    _make("a", triggers=["翻译"]),
    _make("b", patterns=[r"翻译"]),
    _make("c", slots=["翻译"]),
  ]
  result = route_candidates("翻译这段", tools)
  scores = [s for _, s in result]
  assert scores == sorted(scores, reverse=True)


def test_top_k_truncation():
  tools = [_make(f"t{i}", triggers=["翻译"]) for i in range(20)]
  result = route_candidates("翻译", tools, max_candidates=12)
  assert len(result) == 12


def test_empty_when_nothing_matches():
  tools = [_make("translate", triggers=["翻译"])]
  result = route_candidates("今天天气怎么样", tools)
  assert result == []


def test_no_collision_l1_does_not_block_l3():
  """L1 命中翻译时，L3 应仍能召回 search 工具（v3 关键修复）"""
  tools = [
    _make("translate", triggers=["翻译"]),
    _make("search", slots=["来源", "查询", "词源"]),
  ]
  result = route_candidates("帮我查一下翻译这个词的来源", tools)
  names = {t.name for t, _ in result}
  assert "translate" in names
  assert "search" in names
