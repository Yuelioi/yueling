import re

from nonebot import logger
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment

from core.http import get_proxy_client
from services.translate import tran_deepl_pro


async def twitter(bot: Bot, event: GroupMessageEvent, url: str) -> Message | None:
  match = re.search(r"https?://(?:x|twitter)\.com/([0-9A-Za-z_]{1,20})/status/(\d+)", url)
  if not match:
    return None

  username = match.group(1)
  tweet_id = match.group(2)
  api_url = f"https://api.fxtwitter.com/{username}/status/{tweet_id}"

  try:
    async with get_proxy_client() as client:
      resp = await client.get(api_url, timeout=10)
      if resp.status_code != 200:
        logger.warning(f"fxtwitter API 返回 {resp.status_code}: {api_url}")
        return None
      data = resp.json()
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
  header = f"@{screen_name} ({name})\n原文: {text}"
  if translated and translated != text:
    header += f"\n\n翻译: {translated}"

  msg = Message(MessageSegment.text(header))

  if videos:
    video = videos[0]
    if thumb := video.get("thumbnail_url") or video.get("poster"):
      msg += MessageSegment.image(thumb)
    msg += MessageSegment.text("\n视频内容（未下载）")
  else:
    for photo in photos[:4]:
      if photo_url := photo.get("url"):
        msg += MessageSegment.image(photo_url)

  return msg
