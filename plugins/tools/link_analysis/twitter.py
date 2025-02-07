import re

import aiohttp
from nonebot_plugin_alconna import UniMessage


# url = "https://x.com/Aoi_00008/status/1871843879949131866" # 图片文章 不支持
# url = "https://x.com/2024_just19276/status/1850057793048572254" # 视频/图集 支持
async def twitter(url: str):
  if match := re.search(r"https?:\/\/x.com\/[0-9-a-zA-Z_]{1,20}\/status\/([0-9]*)", url):
    x_url = match.group(0)
  else:
    return
  x_url = f"http://47.99.158.118/video-crack/v2/parse?content={x_url}"

  # 内联一个请求
  async def x_req(url):
    async with aiohttp.ClientSession() as session:
      return await session.get(url)

  resp = await x_req(x_url)
  x_data = await resp.json()
  if x_data.get("code") == 0:
    data = x_data.get("data")
    title = data.get("title")
    video_url = data.get("url")
    return UniMessage.text(f"标题：{title}\n视频地址：{video_url}")
