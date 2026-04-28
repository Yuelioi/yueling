"""动漫场景识别 — 核心函数 + 双入口"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.plugin import PluginMetadata

from core.deps import Img
from core.handler import register_handler
from core.http import get_proxy_client
from services import text_to_image
from services.external_api import fetch_image_from_url_ssl
from core.context import ToolContext

__plugin_meta__ = PluginMetadata(
  name="动漫识别",
  description="识别图片中的动漫场景",
  usage="""场景识别 + 图片""",
  extra={
    "group": "娱乐",
    "commands": ["场景识别"],
    "tools": [{
      "name": "trace_anime",
      "description": "识别图片中的动漫场景（需要附带图片）",
      "tags": ["image"],
      "examples": ["这是什么番", "搜番", "识别动漫"],
      "negative_examples": ["识别图片文字"],
      "parameters": {},
      "handler": "trace_tool_handler",
    }],
  },
)


# ─── 核心函数 ─────────────────────────────────────────────


async def do_trace(image_url: str) -> list[dict] | None:
  """调用 trace.moe API 搜索动漫场景"""
  file = await fetch_image_from_url_ssl(image_url)
  async with get_proxy_client() as client:
    response = await client.post(
      "https://api.trace.moe/search?anilistInfo",
      content=file.getvalue(),
      headers={"Content-Type": "image/jpeg"},
    )
  if response.status_code != 200:
    return None
  data = response.json()
  return data.get("result", [])


def format_trace_results(results: list[dict]) -> str:
  """格式化搜索结果为文本"""
  if not results:
    return "未识别到动漫"
  lines = []
  for item in results[:3]:
    title = item.get("anilist", {}).get("title", {}).get("native") or "未知"
    episode = item.get("episode", "?")
    _from = item.get("from", 0)
    similarity = round(item.get("similarity", 0) * 100, 1)
    lines.append(f"动漫: {title}")
    lines.append(f"集数: EP{episode} | 时间: {_from:.0f}s | 相似度: {similarity}%")
    lines.append("---")
  return "\n".join(lines)


# ─── NoneBot 命令入口 ─────────────────────────────────────


trace = on_command("场景识别")


async def image_trace(img=Img(required=True)):
  results = await do_trace(img)
  if not results:
    return "获取数据失败"

  output = []
  for item in results[:5]:
    title = item.get("anilist", {}).get("title", {}).get("native") or "未知"
    episode = item.get("episode", "?")
    _from = item.get("from", 0)
    output.extend([f"标题: {title}", f"集数: {episode} | 时间点: {_from:.0f}s", "---------------------------"])

  return MessageSegment.image(file=text_to_image(output))


register_handler(trace, image_trace)


# ─── AI Tool 入口 ─────────────────────────────────────────


async def trace_tool_handler(ctx: ToolContext) -> str:
  imgs = ctx.get_images()
  if not imgs:
    return "请在消息中附带图片"
  results = await do_trace(imgs[0])
  return format_trace_results(results) if results else "搜番服务不可用"
