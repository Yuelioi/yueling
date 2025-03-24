from nonebot import on_command
from nonebot.plugin import PluginMetadata

from common.base.Handle import register_handler
from plugins.random.rename.data_source import group_change_name

__plugin_meta__ = PluginMetadata(
  name="随机取名",
  description="随机取群昵称",
  usage="""随机取名""",
  extra={"group": "随机", "commands": ["随机取名"]},
)


rename = on_command("随机取名")

register_handler(rename, group_change_name)
