"""翻译命令 — 协议薄壳，业务在 services.translate"""

from nonebot import on_command
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from core.deps import Args
from core.handler import register_handler
from services.translate import SUPPORTED_LANGS, translate as svc_translate

__plugin_meta__ = PluginMetadata(
  name="翻译",
  description="翻译、中英互译、日英互译、日中互译、英日互译",
  usage="""翻译/中译英/中译日/英译中/英译日/日译英/日译中 + 需要翻译的内容""",
  extra={
    "group": "工具",
    "commands": ["翻译", "中译英", "中译日", "英译中", "英译日", "日译英", "日译中"],
  },
)

translator = on_command("翻译", aliases={"中译英", "中译日", "英译中", "英译日", "日译英", "日译中"})


async def _handle(cmd: str = RawCommand(), args: list[str] = Args(0, 999)):
  if not args:
    return "请输入需要翻译的内容"

  if cmd.endswith("译英"):
    target = "en"
  elif cmd.endswith("译日"):
    target = "ja"
  elif cmd.endswith("译中"):
    target = "zh"
  else:
    target = "zh"
    if len(args) >= 2 and args[0].lower() in SUPPORTED_LANGS:
      target = args[0].lower()
      args = args[1:]

  text = " ".join(args).strip()
  if not text:
    return "请输入需要翻译的内容"

  return await svc_translate(text, target=target)


register_handler(translator, _handle)
