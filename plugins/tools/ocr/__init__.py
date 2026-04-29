"""OCR 文字识别 — 双入口（命令 + AI 工具）"""

from nonebot import on_command
from nonebot.plugin import PluginMetadata

from core.deps import Arg, Img
from services.ocr import do_ocr

__plugin_meta__ = PluginMetadata(
  name="OCR",
  description="识别图片里的文字",
  usage="""ocr [中文/日语/英文] + [图片]""",
  extra={
    "group": "工具",
    "commands": ["ocr"],
  },
)

LANG_MAP = {"中文": "chi_sim", "英文": "eng", "日语": "jpn", "日文": "jpn"}


# ─── NoneBot 命令入口 ──────────────────────────────────────

ocr = on_command("ocr")


@ocr.handle()
async def _(img=Img(required=True), lang=Arg()):
  language = LANG_MAP.get(lang, "chi_sim")
  result = await do_ocr(img, language)
  await ocr.finish(result)
