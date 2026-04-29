import asyncio

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.plugin import PluginMetadata

from services import text_to_image
from plugins.funny.hot.utils import baidu, bilibili, weibo, zhihu

__plugin_meta__ = PluginMetadata(
  name="新闻热搜",
  description="获取各大平台热搜",
  usage="""查热搜""",
  extra={
    "group": "娱乐",
    "commands": ["查热搜"],
  },
)

hot = on_fullmatch("查热搜")


@hot.handle()
async def get_hots():
  results = await asyncio.gather(weibo(), bilibili(), baidu(), zhihu())
  lines = [
    "---------微博热搜---------", *(results[0] or []),
    "---------B站热搜---------", *(results[1] or []),
    "---------百度热搜---------", *(results[2] or []),
    "---------知乎热搜---------", *(results[3] or []),
  ]
  img = text_to_image(lines)
  await hot.finish(MessageSegment.image(file=img))
