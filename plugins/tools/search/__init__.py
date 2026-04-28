from nonebot import on_command
from nonebot.plugin import PluginMetadata

from core.deps import Args
from core.handler import register_handler
from core.context import ToolContext
from plugins.tools.search.ae import search_ae_plugin


__plugin_meta__ = PluginMetadata(
  name="搜索工具",
  description="搜索AE插件/脚本",
  usage="""搜ae插件 [关键词]""",
  extra={
    "group": "工具",
    "commands": ["搜ae插件", "搜ae脚本"],
    "tools": [{
      "name": "search_ae",
      "description": "搜索 After Effects 插件或脚本",
      "tags": ["search"],
      "examples": ["搜ae插件 Trapcode", "搜ae脚本 motion"],
      "parameters": {
        "keyword": {"type": "string", "description": "搜索关键词"},
      },
      "handler": "search_tool_handler",
    }],
  },
)


search = on_command("搜ae插件", aliases={"搜ae脚本"})


async def search_handler(args=Args()):
  content = " ".join(args)
  if not content:
    return "请输入搜索关键词"
  return await search_ae_plugin(content)


register_handler(search, search_handler)


async def search_tool_handler(ctx: ToolContext, keyword: str) -> str:
  result = await search_ae_plugin(keyword)
  return result or "未找到相关内容"
