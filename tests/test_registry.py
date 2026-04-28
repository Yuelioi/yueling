"""测试 AI 工具注册和 schema 生成"""

from ai.registry import ToolMeta, ToolRegistry, _build_parameters, _parse_docstring_args, tool


def test_parse_docstring_args():
  doc = """Do something useful.

  Args:
    name: The user's name
    count: How many times to repeat
  """
  result = _parse_docstring_args(doc)
  assert result == {"name": "The user's name", "count": "How many times to repeat"}


def test_parse_docstring_empty():
  assert _parse_docstring_args("") == {}
  assert _parse_docstring_args("No args section here") == {}


def test_build_parameters():
  async def sample_func(ctx, text: str, count: int = 3):
    """Sample.

    Args:
      text: The input text
      count: Repeat count
    """
    pass

  params = _build_parameters(sample_func)
  assert "text" in params
  assert params["text"]["type"] == "string"
  assert "ctx" not in params
  assert params["count"]["type"] == "integer"
  assert params["count"]["default"] == 3


def test_tool_meta_schema():
  meta = ToolMeta(
    name="test_tool",
    description="A test tool",
    parameters={"query": {"type": "string", "description": "Search query"}},
  )
  schema = meta.to_openai_schema()
  assert schema["type"] == "function"
  assert schema["function"]["name"] == "test_tool"
  assert schema["function"]["parameters"]["properties"]["query"]["type"] == "string"
  assert "query" in schema["function"]["parameters"]["required"]


def test_tool_meta_schema_with_default():
  meta = ToolMeta(
    name="test",
    description="test",
    parameters={
      "required_arg": {"type": "string"},
      "optional_arg": {"type": "integer", "default": 5},
    },
  )
  schema = meta.to_openai_schema()
  assert "required_arg" in schema["function"]["parameters"]["required"]
  assert "optional_arg" not in schema["function"]["parameters"]["required"]


def test_registry_crud():
  reg = ToolRegistry()
  meta = ToolMeta(name="foo", description="Foo tool", tags=["test", "fun"])
  reg.register(meta)

  assert reg.get_by_name("foo") == meta
  assert reg.get_by_name("nonexistent") is None
  assert meta in reg.get_all()
  assert meta in reg.get_by_tags({"test"})
  assert meta not in reg.get_by_tags({"unrelated"})


def test_tool_decorator():
  # 手动注册代替全局 registry 的 decorator
  @tool(tags=["math"], examples=["calculate 1+1"])
  async def calculate(ctx, expression: str):
    """Calculate a math expression.

    Args:
      expression: The math expression to evaluate
    """
    pass

  from ai.registry import registry
  meta = registry.get_by_name("calculate")
  assert meta is not None
  assert meta.tags == ["math"]
  assert "expression" in meta.parameters
