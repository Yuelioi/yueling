from services import tran_deepl_pro
from nonebot import on_command
from nonebot.params import RawCommand
from core.deps import Args
from core.context import ToolContext


from nonebot.plugin import PluginMetadata

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


@translator.handle()
async def translate(cmd=RawCommand(), args: list[str] = Args()):
  if not args:
    return "请输入需要翻译的内容"
  if cmd.endswith("译英"):
    target_lang = "en-US"
  elif cmd.endswith("译日"):
    target_lang = "ja"
  else:
    target_lang = "zh"
  res = tran_deepl_pro(" ".join(args), target_lang=target_lang)
  await translator.finish(res)


async def translate_tool_handler(ctx: ToolContext, text: str, target_lang: str = "zh") -> str:
  """AI 工具调用入口"""
  result = tran_deepl_pro(text, target_lang=target_lang)
  return result or "翻译失败"
