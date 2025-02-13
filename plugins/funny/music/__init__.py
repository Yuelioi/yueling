import aiohttp
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_alconna import Alconna, on_alconna

from common.Alc.Alc import pm, ptc

__plugin_meta__ = pm(
  name="点歌",
  description="网易云点歌",
  usage="""点歌 + 歌曲关键词""",
  group="娱乐",
)

_music = Alconna("点歌")
_music.meta = ptc(__plugin_meta__)
music = on_alconna(_music)


@music.handle()
async def _(arg: str):
  return "维护中"
  url = "https://api.xingzhige.com/API/NetEase_CloudMusic_new/"
  params = {"name": arg, "n": 1}

  async with aiohttp.ClientSession() as session:
    async with session.post(url, params=params) as response:
      if response.status == 200:
        data = await response.json()

        data = data["data"]

        await music.finish(
          MessageSegment.music_custom(url=data["songurl"], audio=data["src"], title=data["songname"], content=data["name"], img_url=data["cover"])
        )
