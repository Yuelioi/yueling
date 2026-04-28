from io import BytesIO

from core.config import config
from core.http import get_proxy_client, get_client


async def download_img_proxy(url, proxy=False):
  if proxy and config.proxy.url:
    async with get_proxy_client() as client:
      response = await client.get(url)
      if response.status_code == 200:
        image_bytes = BytesIO(response.content)
        image_bytes.seek(0)
        return image_bytes
  else:
    client = get_client()
    response = await client.get(url)
    if response.status_code == 200:
      image_bytes = BytesIO(response.content)
      image_bytes.seek(0)
      return image_bytes
