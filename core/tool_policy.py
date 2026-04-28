"""Tool Policy — 同语义工具的优先级 / 替换策略。

一期仅占位，dispatcher 不消费此模块。二期实现 alias → tool 选择。

例：
TOOL_POLICY = {
  "translate": ["translate_v2", "translate_basic"],
}
"""

TOOL_POLICY: dict[str, list[str]] = {}


def resolve_alias(alias: str, available_names: set[str]) -> str | None:
  """返回 alias 下首个可用工具名。一期不被调用。"""
  for name in TOOL_POLICY.get(alias, []):
    if name in available_names:
      return name
  return None
