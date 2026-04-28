"""service 层禁止依赖 nonebot/ai/plugins"""

import ast
from pathlib import Path

import pytest

SERVICE_FILE = Path(__file__).parent.parent / "services" / "translate.py"


def _imports_in(file: Path) -> list[str]:
  tree = ast.parse(file.read_text(encoding="utf-8"))
  out: list[str] = []
  for node in ast.walk(tree):
    if isinstance(node, ast.Import):
      out.extend(a.name for a in node.names)
    elif isinstance(node, ast.ImportFrom) and node.module:
      out.append(node.module)
  return out


def test_service_does_not_import_nonebot_ai_plugins():
  imports = _imports_in(SERVICE_FILE)
  banned = ("nonebot", "ai", "plugins")
  for imp in imports:
    assert not any(imp == b or imp.startswith(b + ".") for b in banned), (
      f"service 不应 import {imp}"
    )


@pytest.mark.asyncio
async def test_translate_returns_string():
  from services.translate import translate
  result = await translate("hello", target="zh")
  assert isinstance(result, str)
  assert len(result) > 0
