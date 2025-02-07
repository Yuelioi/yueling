from nonebot_plugin_alconna import Arparma, on_alconna

from common.Alc.Alc import args, pm, ptc, register_handler
from common.utils import tran_deepl_pro

__plugin_meta__ = pm(
  name="翻译",
  description="翻译、中英互译、日英互译、日中互译、英日互译",
  usage="""翻译/中译英/中译日/英译中/英译日/日译英/日译中 + 需要翻译的内容""",
  group="工具",
)

_translator = args("翻译", meta=ptc(__plugin_meta__))
translator = on_alconna(_translator, aliases={"中译英", "中译日", "英译中", "英译日", "日译英", "日译中"})


# 翻译 / 中译英 / 中译日 / 日译英 / 英译日 / 日译英
async def translate(result: Arparma, args: list[str] = []):
  cmd = str(result.header_match.origin)
  if not args:
    return "请输入需要翻译的内容"
  if cmd.endswith("译英"):
    target_lang = "en-US"
  elif cmd.endswith("译日"):
    target_lang = "ja"
  else:
    target_lang = "zh"
  res = tran_deepl_pro(" ".join(args), target_lang=target_lang)
  return res


register_handler(translator, translate)
