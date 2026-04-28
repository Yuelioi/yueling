"""通用 HTTP 数据抓取"""

import io

from core.http import get_client, get_proxy_client, USER_AGENT


async def fetch_json(url: str):
  client = get_client()
  response = await client.get(url)
  if response.status_code == 200:
    return response.json()
  raise TimeoutError


async def fetch_text(url: str):
  client = get_client()
  response = await client.get(url)
  if response.status_code == 200:
    return response.text
  raise TimeoutError


async def fetch_image(url: str, headers=None, *, proxy: bool = False):
  _headers = headers or {"User-Agent": USER_AGENT}

  if proxy:
    async with get_proxy_client() as client:
      response = await client.get(url, headers=_headers)
      if response.status_code == 200:
        return io.BytesIO(response.content)
  else:
    client = get_client()
    response = await client.get(url, headers=_headers)
    if response.status_code == 200:
      return io.BytesIO(response.content)

  raise TimeoutError
