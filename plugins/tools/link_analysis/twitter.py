import re
import tempfile
from datetime import datetime

import aiohttp
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from common.utils import api
from common.utils.translate import tran_deepl_pro


# url = "https://x.com/Aoi_00008/status/1871843879949131866" # 图片文章 不支持
# url = "https://x.com/2024_just19276/status/1850057793048572254" # 视频/图集 支持
async def twitter(bot: Bot, event: GroupMessageEvent, url: str):
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

    bio = await api.fetch_image_from_url(video_url, None, proxy="http://127.0.0.1:10808")

    with tempfile.NamedTemporaryFile(mode="wb", delete=True, suffix=".mp4") as temp_file:
      bio.seek(0)
      temp_file.write(bio.read())
      temp_file_path = temp_file.name

      traned = tran_deepl_pro(title)

      now = datetime.now().strftime("%Y%m%d%H%M%S")
      await bot.call_api("send_group_msg", group_id=event.group_id, message={"type": "text", "data": {"text": f"原文:{title}\n\n翻译:{traned}"}})
      await bot.call_api("upload_group_file", group_id=event.group_id, file=temp_file_path, name=f"{now}.mp4")

    return
