from pathlib import Path

import nonebot
from nonebot.plugin import Plugin

plugins_path = Path(__file__).parent.parent / "plugins"


def load_sub_plugins(parent: str | None = None, *names: str) -> set[Plugin]:
  mods: set[Plugin] = set()

  for name in names:
    if parent:
      p = nonebot.load_plugin(plugins_path / parent / name / "__init__.py")
    else:
      p = nonebot.load_plugin(plugins_path / name / "__init__.py")
    if p:
      mods.add(p)

  return mods


load_mods = load_sub_plugins
