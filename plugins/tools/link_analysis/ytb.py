import re

import aiohttp
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from common.config import config
from common.utils import download_img_proxy, text_to_image, tran_deepl_pro


async def get_ytb_info(video_id: str, api_key: str):
  url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
  async with aiohttp.ClientSession() as session:
    async with session.get(url, proxy="http://127.0.0.1:10809") as response:
      if response.status == 200:
        data = await response.json()

        title = data["items"][0]["snippet"]["title"]
        des = data["items"][0]["snippet"]["description"].replace("\n", "|")
        description = tran_deepl_pro(des)
        assert description
        description = description.replace("|", "\n")
        if len(description) > 200:
          description = f"{description[:200]}......"
        thumbnail_url = data["items"][0]["snippet"]["thumbnails"]["standard"]["url"]

        if res := await download_img_proxy(thumbnail_url, True):
          img2 = text_to_image(
            [
              f"链接：https://www.youtube.com/watch?v={video_id}",
              f"标题：{title}",
              "简介：{description}",
            ]
          )
          return MS.image(res) + MS.image(img2)


async def youtube(url):
  youtube_key = config.api_cfg.youtube_api_keys[0]
  pattern = r"(?<=youtube\.com\/watch\?v=)[^&]+"
  if match := re.search(pattern, url):
    video_id = match[0]
    msgs = await get_ytb_info(video_id, youtube_key)
    try:
      if msgs:
        return msgs
    except Exception:
      return "ytb_获取失败喵"
