"""验证 ToolMeta 新字段和 ai_tool 装饰器"""

import re

from ai.registry import ToolMeta, ai_tool, registry, tool


def test_tool_meta_has_new_fields():
  m = ToolMeta(name="x", description="d")
  assert m.triggers == []
  assert m.patterns == []
  assert m.semantic_slots == []
  assert m.alias is None
  assert m.allow_partial is False


def test_tool_meta_compiled_patterns():
  m = ToolMeta(name="x", description="d", patterns=[r"翻译.*"])
  compiled = m.compiled_patterns
  assert len(compiled) == 1
  assert isinstance(compiled[0], re.Pattern)
  assert compiled[0].search("帮我翻译这段")


def test_ai_tool_alias_registers_correctly():
  @ai_tool(
    description="测试工具",
    triggers=["测试"],
    semantic_slots=["test", "测试用"],
    alias="testkit",
    allow_partial=True,
  )
  async def _foo_tool_for_test(ctx, x: str) -> str:
    return x

  meta = registry.get_by_name("_foo_tool_for_test")
  assert meta is not None
  assert meta.triggers == ["测试"]
  assert meta.semantic_slots == ["test", "测试用"]
  assert meta.alias == "testkit"
  assert meta.allow_partial is True


def test_legacy_tool_decorator_still_works():
  @tool(tags=["legacy"])
  async def _legacy_tool_for_test(ctx, x: str) -> str:
    """旧装饰器测试"""
    return x

  meta = registry.get_by_name("_legacy_tool_for_test")
  assert meta is not None
  assert meta.tags == ["legacy"]
  assert meta.triggers == []  # 默认空


def test_args_schema_default_none():
  m = ToolMeta(name="x", description="d")
  assert m.args_schema is None


def test_args_schema_pydantic_to_openai_schema():
  from typing import Literal

  from pydantic import BaseModel

  class TestArgs(BaseModel):
    action: Literal["block", "unblock", "list"]
    plugin_name: str | None = None

  @ai_tool(
    description="测试 args_schema",
    args_schema=TestArgs,
  )
  async def _args_schema_test_tool(ctx, args) -> str:
    return ""

  meta = registry.get_by_name("_args_schema_test_tool")
  assert meta is not None
  assert meta.args_schema is TestArgs

  schema = meta.to_openai_schema()
  params = schema["function"]["parameters"]
  assert params["type"] == "object"
  assert "action" in params["properties"]
  assert "enum" in params["properties"]["action"]
  assert set(params["properties"]["action"]["enum"]) == {"block", "unblock", "list"}
  assert "action" in params["required"]
  assert "plugin_name" not in params["required"]
