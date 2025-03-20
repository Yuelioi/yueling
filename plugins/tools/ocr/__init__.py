import aiohttp
from nonebot import on_command
from nonebot.plugin import PluginMetadata

from common.base.Depends import Arg, Img
from common.utils import api

__plugin_meta__ = PluginMetadata(name="ocr", description="识别图片里的文字", usage="""ocr [中文/日语/英文] + [图片]""", extra={"group": "工具"})


ocr = on_command("ocr")


@ocr.handle()
async def _(img=Img(required=True), language=Arg()):
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
