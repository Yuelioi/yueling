"""OCR 文字识别 — 核心函数 + 双入口"""

from nonebot import on_command
from nonebot.plugin import PluginMetadata

from core.deps import Arg, Img
from core.config import config
from core.http import get_client
from services.external_api import fetch_image_from_url_ssl
from core.context import ToolContext

__plugin_meta__ = PluginMetadata(
  name="OCR",
  description="识别图片里的文字",
  usage="""ocr [中文/日语/英文] + [图片]""",
  extra={
    "group": "工具",
    "commands": ["ocr"],
    "tools": [{
      "name": "ocr_image",
      "description": "识别图片中的文字(需要消息附带图片)",
      "tags": ["image", "ocr"],
      "examples": ["识别图片文字", "OCR", "帮我看看图里写了什么"],
      "negative_examples": ["识别动漫角色"],
      "parameters": {
        "language": {"type": "string", "description": "语言(chi_sim/eng/jpn)", "default": "chi_sim"},
      },
      "handler": "ocr_tool_handler",
    }],
  },
)

LANG_MAP = {"中文": "chi_sim", "英文": "eng", "日语": "jpn", "日文": "jpn"}

# ─── 核心函数（不依赖框架）────────────────────────────────────


async def do_ocr(image_url: str, language: str = "chi_sim") -> str:
  """执行 OCR，返回识别文本"""
  file = await fetch_image_from_url_ssl(image_url)
  client = get_client()
  response = await client.post(
    config.api.ocr_url,
    files={"file": ("image.jpg", file.getvalue(), "image/jpeg")},
    data={"language": language},
  )
  if response.status_code == 200:
    return response.json().get("data", "").strip() or "未识别出文字"
  return "OCR 服务不可用"


# ─── NoneBot 命令入口 ──────────────────────────────────────


ocr = on_command("ocr")


@ocr.handle()
async def _(img=Img(required=True), lang=Arg()):
  language = LANG_MAP.get(lang, "chi_sim")
  result = await do_ocr(img, language)
  await ocr.finish(result)


# ─── AI Tool 入口 ─────────────────────────────────────────


async def ocr_tool_handler(ctx: ToolContext, language: str = "chi_sim") -> str:
  imgs = ctx.get_images()
  if not imgs:
    return "请在消息中附带图片"
  return await do_ocr(imgs[0], language)
