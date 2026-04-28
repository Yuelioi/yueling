from nonebot.plugin import PluginMetadata

from core.plugin import load_mods

__plugin_meta__ = PluginMetadata(
  name="yueling",
  description="",
  usage="",
)

__version__ = "1.0.0"


sub_plugins = load_mods("game", *["pk", "jw3"])
