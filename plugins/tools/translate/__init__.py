"""翻译命令 — 协议薄壳，业务在 services.translate"""

from nonebot import on_command
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from core.context import ToolContext
from core.deps import Args
from core.handler import register_handler
from services.translate import translate as svc_translate

__plugin_meta__ = PluginMetadata(
  name="翻译",
  description="翻译、中英互译、日英互译、日中互译、英日互译",
  usage="""翻译/中译英/中译日/英译中/英译日/日译英/日译中 + 需要翻译的内容""",
  extra={
    "group": "工具",
    "commands": ["翻译", "中译英", "中译日", "英译中", "英译日", "日译英", "日译中"],
    "tools": [{
      "name": "translate",
      "description": "翻译文本到目标语言",
      "tags": ["language"],
      "examples": ["翻译 hello world", "把这段翻译成英文", "这句话日语怎么说"],
      "negative_examples": ["翻译一下这个图片"],
      "parameters": {
        "text": {"type": "string", "description": "要翻译的文本"},
        "target_lang": {"type": "string", "description": "目标语言代码: zh/en-US/ja", "default": "zh"},
      },
      "handler": "translate_tool_handler",
    }],
  },
)

translator = on_command("翻译", aliases={"中译英", "中译日", "英译中", "英译日", "日译英", "日译中"})


async def _handle(cmd: str = RawCommand(), args: list[str] = Args(0, 999)):
  if not args:
    return "请输入需要翻译的内容"

  # 别名 (中译英/日译中 等) 通过命令后缀决定目标语言；裸 "翻译" 命令支持
  # 第一个参数为 2-5 字符的纯字母语言代码
  if cmd.endswith("译英"):
    target = "en"
  elif cmd.endswith("译日"):
    target = "ja"
  elif cmd.endswith("译中"):
    target = "zh"
  else:
    target = "zh"
    if args and len(args[0]) <= 5 and args[0].isalpha():
      target = args[0].lower()
      args = args[1:]

  text = " ".join(args).strip()
  if not text:
    return "请输入需要翻译的内容"

  return await svc_translate(text, target=target)


register_handler(translator, _handle)


async def translate_tool_handler(ctx: ToolContext, text: str, target_lang: str = "zh") -> str:
  """AI 工具调用入口"""
  result = await svc_translate(text, target=target_lang)
  return result or "翻译失败"
