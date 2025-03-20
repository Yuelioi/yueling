from common.base.Handle import register_handler
from common.config import config
from common.utils.content_convert import text_to_image
from plugins.system.plugin.manager import hm
from nonebot import on_command

from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.plugin import PluginMetadata

from common.base.Depends import Arg


__plugin_meta__ = PluginMetadata(
  name="系统帮助",
  description="帮助",
  usage="""help + 分组
  help + id
  help + 名称
""",
  extra={"group": "系统", "commands": ["help", "帮助"]},
)


help = on_command("帮助")


async def hp(commond: str = Arg()):
  if commond:
    return hm.search(commond)

  help_img_path = config.resource.tmp / "help.jpg"

  if not help_img_path.exists():
    help_img_path.write_bytes(text_to_image(hm.all_help()).getvalue())

  return MessageSegment.image(file=help_img_path)


register_handler(help, hp)
