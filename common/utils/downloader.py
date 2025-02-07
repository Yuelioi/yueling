from io import BytesIO

import aiohttp


async def download_img_proxy(url, proxy=False):
  params = {"url": url, "proxy": "http://127.0.0.1:10809" if proxy else ""}

  async with aiohttp.ClientSession() as session:
    async with session.get(**params) as response:
      if response.status == 200:
        image_data = await response.read()
        image_bytes = BytesIO(image_data)
        image_bytes.seek(0)
        return image_bytes
