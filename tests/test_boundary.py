"""跨层 import 边界测试：验证 services/ 和 ai/tools/ 的 import 约束"""

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


def _imports_in(file: Path) -> list[str]:
  tree = ast.parse(file.read_text(encoding="utf-8"))
  out: list[str] = []
  for node in ast.walk(tree):
    if isinstance(node, ast.Import):
      out.extend(a.name for a in node.names)
    elif isinstance(node, ast.ImportFrom) and node.module:
      out.append(node.module)
  return out


def _collect_py_files(directory: Path) -> list[Path]:
  return sorted(directory.glob("*.py"))


@pytest.mark.parametrize(
  "svc_file",
  _collect_py_files(PROJECT_ROOT / "services"),
  ids=lambda p: p.name,
)
def test_service_does_not_import_nonebot_ai_plugins(svc_file):
  imports = _imports_in(svc_file)
  banned = ("nonebot", "ai", "plugins")
  for imp in imports:
    assert not any(imp == b or imp.startswith(b + ".") for b in banned), (
      f"services/{svc_file.name} should not import {imp}"
    )


@pytest.mark.parametrize(
  "tool_file",
  [f for f in _collect_py_files(PROJECT_ROOT / "ai" / "tools") if f.name != "__init__.py"],
  ids=lambda p: p.name,
)
def test_ai_tools_do_not_import_plugins(tool_file):
  try:
    imports = _imports_in(tool_file)
  except SyntaxError:
    pytest.skip(f"{tool_file.name} has syntax error, skipping")
  for imp in imports:
    assert not (imp == "plugins" or imp.startswith("plugins.")), (
      f"ai/tools/{tool_file.name} should not import {imp}"
    )
