import asyncio

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.plugin import PluginMetadata

from services import text_to_image
from core.context import ToolContext
from plugins.funny.hot.utils import baidu, bilibili, weibo, zhihu

__plugin_meta__ = PluginMetadata(
  name="新闻热搜",
  description="获取各大平台热搜",
  usage="""查热搜""",
  extra={
    "group": "娱乐",
    "commands": ["查热搜"],
    "tools": [{
      "name": "get_hot_topics",
      "description": "查询各平台热搜榜(微博/知乎/B站/百度)",
      "tags": ["search", "info"],
      "examples": ["查热搜", "微博热搜", "今天有什么新闻"],
      "parameters": {
        "platform": {"type": "string", "description": "平台(weibo/zhihu/bilibili/baidu/all)", "default": "all"},
      },
      "handler": "hot_tool_handler",
    }],
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


async def hot_tool_handler(ctx: ToolContext, platform: str = "all") -> str:
  handlers = {"weibo": weibo, "zhihu": zhihu, "bilibili": bilibili, "baidu": baidu}
  if platform == "all":
    results = await asyncio.gather(weibo(), bilibili(), baidu(), zhihu())
    lines = []
    for name, data in zip(["微博", "B站", "百度", "知乎"], results):
      lines.append(f"【{name}】")
      lines.extend((data or ["无数据"])[:5])
    return "\n".join(lines)
  handler = handlers.get(platform, weibo)
  data = await handler()
  return "\n".join(data[:10]) if data else "获取失败"
