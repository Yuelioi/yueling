import aiohttp
from bs4 import BeautifulSoup
from nonebot.adapters.onebot.v11.message import MessageSegment

from common.utils.api import fetch_image_from_url
from common.utils.translate import tran_deepl_pro


async def behance(url):
  headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "cookie": "ilo0=1",
  }

  async with aiohttp.ClientSession(headers=headers) as session:
    async with session.get(url, proxy="http://127.0.0.1:10808") as response:
      html = await response.text()
      soup = BeautifulSoup(html, "html.parser")

      # 获取 <title>
      title = None
      if soup.head and soup.head.title and soup.head.title.string:
        title = tran_deepl_pro(soup.head.title.string.strip())

      # 获取 <meta name="description">
      description = None
      if soup.head:
        meta_desc = soup.head.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
          description = tran_deepl_pro(meta_desc["content"].strip().replace(" :: Behance", ""))

      # 获取图片
      image_data = None
      image_url = None
      if soup.head:
        # 尝试 og:image
        meta_image = soup.head.find("meta", property="og:image")
        if meta_image and meta_image.get("content"):
          image_url = meta_image["content"].strip()
        else:
          # fallback: <link rel="image_src">
          link_image = soup.head.find("link", rel="image_src")
          if link_image and link_image.get("href"):
            image_url = link_image["href"].strip()

        if image_url:
          image_data = await fetch_image_from_url(image_url, proxy="http://127.0.0.1:10808")

      if title and description and image_data:
        return MessageSegment.text(f"标题: {title}\n概述: {description}") + MessageSegment.image(file=image_data)
      else:
        return MessageSegment.text(f"标题: {title}\n概述: {description}")
