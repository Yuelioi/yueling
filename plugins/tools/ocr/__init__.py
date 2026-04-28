"""OCR 文字识别 — RapidOCR 本地引擎 + 双入口"""

import asyncio

from nonebot import on_command
from nonebot.plugin import PluginMetadata
from rapidocr_onnxruntime import RapidOCR

from core.deps import Arg, Img
from core.context import ToolContext
from services.http_fetch import fetch_image

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

_engine = RapidOCR()


async def do_ocr(image_url: str, language: str = "chi_sim") -> str:
  """下载图片并执行本地 OCR"""
  img_buf = await fetch_image(image_url)
  img_bytes = img_buf.getvalue()

  result, _ = await asyncio.to_thread(_engine, img_bytes)
  if not result:
    return "未识别出文字"

  lines = [line[1] for line in result]
  return "\n".join(lines).strip() or "未识别出文字"


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
