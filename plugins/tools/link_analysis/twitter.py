import re
import tempfile
from datetime import datetime

import aiohttp
from nonebot import logger
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment

from common.config.config import proxy
from common.utils import api
from common.utils.translate import tran_deepl_pro


async def twitter(bot: Bot, event: GroupMessageEvent, url: str) -> Message | None:
  match = re.search(r"https?://(?:x|twitter)\.com/([0-9A-Za-z_]{1,20})/status/(\d+)", url)
  if not match:
    return None

  username = match.group(1)
  tweet_id = match.group(2)
  api_url = f"https://api.fxtwitter.com/{username}/status/{tweet_id}"

  try:
    async with aiohttp.ClientSession() as session:
      async with session.get(api_url, proxy=proxy or None, timeout=aiohttp.ClientTimeout(total=10)) as resp:
        if resp.status != 200:
          logger.warning(f"fxtwitter API 返回 {resp.status}: {api_url}")
          return None
        data = await resp.json()
  except Exception as e:
    logger.error(f"请求 fxtwitter 失败: {e}")
    return None

  tweet = data.get("tweet")
  if not tweet:
    return None

  author = tweet.get("author", {})
  text = tweet.get("text", "")
  name = author.get("name", username)
  screen_name = author.get("screen_name", username)
  media = tweet.get("media") or {}
  photos = media.get("photos", [])
  videos = media.get("videos", [])

  translated = tran_deepl_pro(text) if text else ""
  header = f"🐦 @{screen_name} ({name})\n原文: {text}"
  if translated and translated != text:
    header += f"\n\n翻译: {translated}"

  msg = Message(MessageSegment.text(header))
  return msg

  # 有视频：下载后上传到群文件
  if videos:
    video = videos[0]
    thumb = video.get("thumbnail_url") or video.get("poster")

   

    if thumb:
      msg += MessageSegment.image(thumb)

    msg += MessageSegment.text("\n🎬 视频内容（未下载）")
    return msg

  # 无视频：文字 + 图片（最多4张）
  msg = Message(MessageSegment.text(header))
  for photo in photos[:4]:
    if photo_url := photo.get("url"):
      msg += MessageSegment.image(photo_url)

  return msg
