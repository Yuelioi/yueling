import aiohttp
from nonebot_plugin_alconna import Alconna, Args, Image, on_alconna
from nonebot_plugin_alconna.builtins.extensions.reply import ReplyMergeExtension

from common.Alc.Alc import pm, ptc
from common.utils import api

__plugin_meta__ = pm(
  name="ocr",
  description="识别图片里的文字",
  usage="""ocr [中文/日语/英文] + [图片]""",
  group="工具",
)

meta = ptc(__plugin_meta__)
_ocr = Alconna("ocr", Args["language?", str]["img", Image], meta=meta)
ocr = on_alconna(_ocr, extensions=[ReplyMergeExtension])


@ocr.handle()
async def _(img: Image, language: str = "chi_sim"):
  async with aiohttp.ClientSession() as session:
    if not img.url:
      return

    dic = {"中文": "chi_sim", "英文": "eng", "日语": "jpn", "日文": "jpn"}
    language = dic.get(language, "chi_sim")

    file = await api.fetch_image_from_url_ssl(img.url)

    form_data = aiohttp.FormData()
    form_data.add_field("language", language)
    form_data.add_field("file", file, filename="image.jpg", content_type="image/jpeg")

    async with session.post("https://api.yuelili.com/ocr/ocr", data=form_data) as response:
      if response.status == 200:
        result = await response.json()
        data = result.get("data").strip()
        if data:
          await ocr.finish(data)
        await ocr.finish("未识别出文字, 或者切换语言尝试")
