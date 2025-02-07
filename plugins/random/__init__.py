from nonebot.plugin import PluginMetadata

from common.base.Plugin import load_mods

__plugin_meta__ = PluginMetadata(
  name="yueling",
  description="",
  usage="",
)

__version__ = "1.0.0"


sub_plugins = load_mods(
  "random",
  *["daily", "emoticon", "image", "member", "quotation", "rename", "roll"],
)
