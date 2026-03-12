from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata

from common.base.Depends import Arg

__plugin_meta__ = PluginMetadata(
  name="看电视",
  description="通过qq打开电脑链接(需要本地安装app)",
  usage="""看电视 + 链接""",
  extra={"group": "娱乐", "commands": ["看电视"]},
)


watch = on_command("看电视")


@watch.handle()
async def _watch_tv(event: GroupMessageEvent, link: str = Arg()):
  await watch.finish("维护中")
