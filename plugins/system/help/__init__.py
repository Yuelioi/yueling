from nonebot import require
from nonebot_plugin_alconna import UniMessage, on_alconna

from common.Alc.Alc import arg, pm, ptc, register_handler

require("plugins.system.plugin")
from common.config import config
from common.utils.content_convert import text_to_image
from plugins.system.plugin.manager import hm

__plugin_meta__ = pm(
  name="系统帮助",
  description="帮助",
  usage="""help + 分组
  help + id
  help + 名称
""",
  group="系统",
)

_help = arg("help", required=False, meta=ptc(__plugin_meta__))

help = on_alconna(_help, aliases={"帮助"})


async def hp(arg: str = ""):
  if arg:
    return hm.search(arg)

  help_img_path = config.resource.tmp / "help.jpg"

  if not help_img_path.exists():
    help_img_path.write_bytes(text_to_image(hm.all_help()).getvalue())

  return UniMessage.image(path=help_img_path)


register_handler(help, hp)
