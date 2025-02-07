from nonebot_plugin_alconna import UniMessage, on_alconna

from common.Alc.Alc import fullmatch, pm, ptc
from common.utils import text_to_image
from plugins.funny.hot.utils import baidu, bilibili, weibo, zhihu

__plugin_meta__ = pm(
  name="新闻热搜",
  description="获取各大平台热搜",
  usage="""查热搜""",
  group="娱乐",
)

_hot = fullmatch("查热搜")
_hot.meta = ptc(__plugin_meta__)
hot = on_alconna(_hot)


@hot.handle()
async def get_hots():
  async def hots():
    weibo_hot = await weibo() or []
    zhihu_hot = await zhihu() or []
    bilibili_hot = await bilibili() or []
    baidu_hot = await baidu() or []

    return [
      "---------微博热搜---------",
      *weibo_hot,
      "---------B站热搜---------",
      *bilibili_hot,
      "---------百度热搜---------",
      *baidu_hot,
      "---------知乎热搜---------",
      *zhihu_hot,
    ]

  img = text_to_image(await hots())
  await hot.finish(UniMessage.image(raw=img))
