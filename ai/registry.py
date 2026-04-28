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

  def to_openai_schema(self) -> dict:
    return {
      "type": "function",
      "function": {
        "name": self.name,
        "description": self.description,
        "parameters": {
          "type": "object",
          "properties": self.parameters,
          "required": [k for k, v in self.parameters.items() if "default" not in v],
        },
      },
    }


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


def tool(
  tags: list[str] | None = None,
  examples: list[str] | None = None,
  negative_examples: list[str] | None = None,
  permission: str = "member",
  risk_level: str = "low",
  confirm_required: bool = False,
):
  def decorator(func: Callable):
    doc = func.__doc__ or ""
    first_line = doc.strip().split("\n")[0] if doc.strip() else func.__name__
    parameters = _build_parameters(func)

    meta = ToolMeta(
      name=func.__name__,
      description=first_line,
      tags=tags or [],
      examples=examples or [],
      negative_examples=negative_examples or [],
      parameters=parameters,
      permission=permission,
      risk_level=risk_level,
      confirm_required=confirm_required,
      func=func,
    )
    registry.register(meta)
    return func

  return decorator
