from bs4 import BeautifulSoup
from nonebot.adapters.onebot.v11.message import MessageSegment

from core.http import get_proxy_client
from services.translate import tran_deepl_pro


async def behance(url):
  headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "cookie": "ilo0=1",
  }

  async with get_proxy_client() as client:
    response = await client.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    title = None
    if soup.head and soup.head.title and soup.head.title.string:
      title = tran_deepl_pro(soup.head.title.string.strip())

    description = None
    if soup.head:
      meta_desc = soup.head.find("meta", attrs={"name": "description"})
      if meta_desc and meta_desc.get("content"):
        description = tran_deepl_pro(meta_desc["content"].strip().replace(" :: Behance", ""))

    image_data = None
    image_url = None
    if soup.head:
      meta_image = soup.head.find("meta", property="og:image")
      if meta_image and meta_image.get("content"):
        image_url = meta_image["content"].strip()
      else:
        link_image = soup.head.find("link", rel="image_src")
        if link_image and link_image.get("href"):
          image_url = link_image["href"].strip()

      if image_url:
        img_resp = await client.get(image_url)
        if img_resp.status_code == 200:
          from io import BytesIO
          image_data = BytesIO(img_resp.content)

    if title and description and image_data:
      return MessageSegment.text(f"标题: {title}\n概述: {description}") + MessageSegment.image(file=image_data)
    else:
      return MessageSegment.text(f"标题: {title}\n概述: {description}")
