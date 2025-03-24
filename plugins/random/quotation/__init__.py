from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata

from common.base.Depends import Arg
from common.base.Handle import register_handler
from common.utils import get_random_image

__plugin_meta__ = PluginMetadata(
  name="语录",
  description="语录",
  usage="""语录 [群友名]""",
  extra={"group": "随机", "commands": ["语录"]},
)


quotation = on_command(
  "语录",
)


@quotation.handle()
async def quotation_handle(event: GroupMessageEvent, nickname=Arg()):
  folder = "语录"

  white_list = ["玉米", "甜甜"]

  if nickname in white_list:
    random_file = get_random_image(folder, keyword=f"{nickname}")
  else:
    random_file = get_random_image(folder, keyword=f"{event.group_id}_{nickname}")

  if random_file:
    return random_file
  else:
    return "尚未添加此人语录"


register_handler(quotation, quotation_handle)
