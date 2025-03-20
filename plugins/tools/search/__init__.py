from nonebot import on_message
from common.base.Depends import Args
from plugins.tools.search.ae import search_ae_plugin

from nonebot.plugin import PluginMetadata


__plugin_meta__ = PluginMetadata(
  name="搜索工具",
  description="搜索各种内容",
  usage="""搜ae插件/百度百科/wiki [内容]""",
  extra={
    "group": "工具",
  },
)


search = on_message()

search_types = ["ae插件", "ae脚本"]


def extract_search(query: str):
  for search_type in search_types:
    if search_type in query:
      content = query.replace(search_type, "").strip()
      return search_type, content
  return None, query.strip()


async def search_all(args=Args()):
  msg = " ".join(args)

  if not msg.startswith(("搜", "搜索")):
    return

  msgs = msg.replace("搜索", "").replace("搜", "").strip()

  _type, content = extract_search(msgs)
  if not _type:
    return

  if not content:
    return "请输入搜索内容"

  if _type in ["ae插件", "ae脚本"]:
    return await search_ae_plugin(content)
