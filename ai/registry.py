import inspect
import re
from dataclasses import dataclass, field
from typing import Any, Callable



@dataclass
class ToolMeta:
  name: str
  description: str
  tags: list[str] = field(default_factory=list)
  examples: list[str] = field(default_factory=list)
  negative_examples: list[str] = field(default_factory=list)
  parameters: dict[str, Any] = field(default_factory=dict)
  permission: str = "member"
  risk_level: str = "low"
  confirm_required: bool = False
  func: Callable | None = None
  plugin_name: str = ""
  # v3 新增 (本任务)
  triggers: list[str] = field(default_factory=list)
  patterns: list[str] = field(default_factory=list)
  semantic_slots: list[str] = field(default_factory=list)
  alias: str | None = None
  allow_partial: bool = False
  args_schema: type | None = None

  @property
  def compiled_patterns(self) -> list[re.Pattern]:
    if not hasattr(self, "_compiled_patterns_cache"):
      self._compiled_patterns_cache = [re.compile(p) for p in self.patterns]
    return self._compiled_patterns_cache

  def to_openai_schema(self) -> dict:
    if self.args_schema is not None:
      params = _schema_from_pydantic(self.args_schema)
    else:
      params = {
        "type": "object",
        "properties": self.parameters,
        "required": [k for k, v in self.parameters.items() if "default" not in v],
      }
    return {
      "type": "function",
      "function": {
        "name": self.name,
        "description": self.description,
        "parameters": params,
      },
    }


def _schema_from_pydantic(model: type) -> dict[str, Any]:
  schema = model.model_json_schema()
  props = schema.get("properties", {})
  required = schema.get("required", [])
  # Flatten $defs / allOf references for simple Literal enums
  defs = schema.get("$defs", {})
  for key, val in props.items():
    if "$ref" in val:
      ref_name = val["$ref"].rsplit("/", 1)[-1]
      if ref_name in defs:
        props[key] = defs[ref_name]
    if "allOf" in val and len(val["allOf"]) == 1 and "$ref" in val["allOf"][0]:
      ref_name = val["allOf"][0]["$ref"].rsplit("/", 1)[-1]
      if ref_name in defs:
        resolved = dict(defs[ref_name])
        if "default" in val:
          resolved["default"] = val["default"]
        props[key] = resolved
  return {"type": "object", "properties": props, "required": required}


def _parse_docstring_args(docstring: str) -> dict[str, str]:
  descriptions = {}
  if not docstring:
    return descriptions
  in_args = False
  for line in docstring.split("\n"):
    stripped = line.strip()
    if stripped.lower().startswith("args:"):
      in_args = True
      continue
    if in_args:
      if not stripped or (not stripped.startswith(" ") and ":" not in stripped and stripped.endswith(":")):
        break
      match = re.match(r"(\w+)\s*[:：]\s*(.+)", stripped)
      if match:
        descriptions[match.group(1)] = match.group(2).strip()
  return descriptions


TYPE_MAP = {
  int: "integer",
  float: "number",
  str: "string",
  bool: "boolean",
  list: "array",
}


def _build_parameters(func: Callable) -> dict[str, Any]:
  sig = inspect.signature(func)
  hints = func.__annotations__
  doc_args = _parse_docstring_args(func.__doc__ or "")
  params = {}

  for name, param in sig.parameters.items():
    if name == "ctx" or name == "self":
      continue
    hint = hints.get(name, str)
    json_type = TYPE_MAP.get(hint, "string")
    prop: dict[str, Any] = {"type": json_type}
    if name in doc_args:
      prop["description"] = doc_args[name]
    if param.default is not inspect.Parameter.empty:
      prop["default"] = param.default
    params[name] = prop

  return params


class ToolRegistry:
  def __init__(self):
    self._tools: dict[str, ToolMeta] = {}

  def register(self, meta: ToolMeta):
    self._tools[meta.name] = meta

  def get_all(self) -> list[ToolMeta]:
    return list(self._tools.values())

  def get_by_name(self, name: str) -> ToolMeta | None:
    return self._tools.get(name)

  def get_by_tags(self, tags: set[str]) -> list[ToolMeta]:
    return [t for t in self._tools.values() if set(t.tags) & tags]


registry = ToolRegistry()


def ai_tool(
  description: str | None = None,
  tags: list[str] | None = None,
  examples: list[str] | None = None,
  negative_examples: list[str] | None = None,
  triggers: list[str] | None = None,
  patterns: list[str] | None = None,
  semantic_slots: list[str] | None = None,
  alias: str | None = None,
  allow_partial: bool = False,
  args_schema: type | None = None,
  permission: str = "member",
  risk_level: str = "low",
  confirm_required: bool = False,
  name: str | None = None,
):
  """v3 装饰器：与 @tool 共享 registry，但支持新字段。"""

  def decorator(func: Callable):
    doc = func.__doc__ or ""
    first_line = doc.strip().split("\n")[0] if doc.strip() else func.__name__
    if args_schema is not None:
      parameters = _schema_from_pydantic(args_schema).get("properties", {})
    else:
      parameters = _build_parameters(func)

    meta = ToolMeta(
      name=name or func.__name__,
      description=description or first_line,
      tags=tags or [],
      examples=examples or [],
      negative_examples=negative_examples or [],
      parameters=parameters,
      permission=permission,
      risk_level=risk_level,
      confirm_required=confirm_required,
      func=func,
      triggers=triggers or [],
      patterns=patterns or [],
      semantic_slots=semantic_slots or [],
      alias=alias,
      allow_partial=allow_partial,
      args_schema=args_schema,
    )
    registry.register(meta)
    return func

  return decorator
