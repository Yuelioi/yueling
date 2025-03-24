from common.utils import tran_deepl_pro
from nonebot import on_command
from nonebot.params import RawCommand
from common.base.Depends import Args


from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
  name="翻译",
  description="翻译、中英互译、日英互译、日中互译、英日互译",
  usage="""翻译/中译英/中译日/英译中/英译日/日译英/日译中 + 需要翻译的内容""",
  extra={"group": "工具", "commands": ["翻译", "中译英", "中译日", "英译中", "英译日", "日译英", "日译中"]},
)

translator = on_command("翻译", aliases={"中译英", "中译日", "英译中", "英译日", "日译英", "日译中"})


# 翻译 / 中译英 / 中译日 / 日译英 / 英译日 / 日译英
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
