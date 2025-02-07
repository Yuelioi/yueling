import io
import ssl
import urllib.parse

import aiohttp


async def fetch_json_from_url(url: str):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      if response.status == 200:
        return await response.json()

  raise TimeoutError


async def fetch_text_from_url(url: str):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      if response.status == 200:
        return await response.text()

  raise TimeoutError


async def fetch_image_from_url(url: str, headers=None, **params):
  # url = url.replace("multimedia.nt.qq.com.cn", "gchat.qpic.cn")

  _headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
  }
  if headers:
    _headers = headers

  async with aiohttp.ClientSession(headers=_headers) as session:
    async with session.get(url, **params) as response:
      if response.status == 200:
        image_bytes = await response.read()
        image_data = io.BytesIO(image_bytes)
        return image_data
  raise TimeoutError


async def fetch_image_from_url_ssl(url: str, **params):
  # url = url.replace("multimedia.nt.qq.com.cn", "gchat.qpic.cn")

  SSL_CONTEXT = ssl.create_default_context()
  SSL_CONTEXT.set_ciphers("DEFAULT")

  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
  }

  async with aiohttp.ClientSession(headers=headers) as session:
    async with session.get(url, **params, ssl=SSL_CONTEXT) as response:
      if response.status == 200:
        image_bytes = await response.read()
        image_data = io.BytesIO(image_bytes)
        return image_data
  raise TimeoutError


async def download_avatar(user_id: int):
  url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
  data = await fetch_image_from_url(url)
  return data


async def shadiao():
  """沙雕新闻, 返回title content"""
  res = await fetch_json_from_url("https://api.yujn.cn/api/shadiao.php")
  return res["title"], res["content"]


async def xiaoheizi():
  """小黑子, 返回图片数据"""
  return await fetch_image_from_url("http://api.yujn.cn/api/cxk.php")


async def chat(msg: str):
  """遇见聊天,返回str"""

  res = await fetch_text_from_url(f"https://api.yujn.cn/api/moli.php?msg={msg}")
  words = {"遇见": "月灵"}

  for v, k in words.items():
    res = res.replace(v, k)

  return res


async def chi():
  """吃什么"""
  return await fetch_text_from_url("https://api.yujn.cn/api/chi.php")


async def chaijun():
  """随机柴郡图"""
  return await fetch_image_from_url("http://api.yujn.cn/api/chaijun.php")


async def fun_gif():
  """搞笑gif"""
  return await fetch_image_from_url("http://api.yujn.cn/api/gif.php")


async def tiangou():
  """舔狗日记"""
  return await fetch_text_from_url("http://api.yujn.cn/api/tiangou.php")


async def lvcha():
  """绿茶语录"""
  return await fetch_text_from_url("http://api.yujn.cn/api/lvchayy.php")


async def shenhuifu():
  """神回复"""
  return await fetch_text_from_url("http://api.yujn.cn/api/shf.php")


async def kfc():
  """KFC文案"""
  return await fetch_text_from_url("http://api.yujn.cn/api/kfc.php")


async def read60s():
  """获取60s图片"""
  return await fetch_image_from_url("http://api.yujn.cn/api/60SReadWorld.php")


# endregion

# region other other api methods


async def trace(img):
  """动漫搜图"""
  base_url = "https://api.trace.moe/search?cutBorders&anilistInfo&url={}"
  encoded_url = urllib.parse.quote_plus(img)
  full_url = base_url.format(encoded_url)
  return await fetch_json_from_url(full_url)


async def read60s_2():
  data = await fetch_json_from_url("https://api.2xb.cn/zaob")
  return await fetch_image_from_url(data["imageUrl"])


async def get_image_tag(img):
  """获取图片标签
  https://portal.vision.cognitive.azure.com/demo/generic-image-tagging
  """
  base_url = "https://portal.vision.cognitive.azure.com/api/demo/analyze?features=tags&language=zh"


# endregion other


import asyncio

import aiohttp
from bs4 import BeautifulSoup, NavigableString, Tag


def extract_content(node: Tag | NavigableString | None):
  if isinstance(node, Tag):
    content = node.get("content")
    if content is None:
      return ""

    if isinstance(content, str):
      return content.strip()
    else:
      return "\n".join(content).strip()
  elif isinstance(node, NavigableString):
    return node.strip()
  return ""


async def get_html(url: str):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      if response.status == 200:
        return await response.text()


async def get_title(html: str):
  soup = BeautifulSoup(html, "html.parser")
  return soup.title.string if soup.title else None


async def get_summary(html: str):
  soup = BeautifulSoup(html, "html.parser")
  summary = soup.find("meta", attrs={"name": "description"})
  if summary is None:
    summary = soup.find("meta", attrs={"property": "og:description"})

  return extract_content(summary)


async def get_keywords(html: str):
  soup = BeautifulSoup(html, "html.parser")
  keywords = soup.find("meta", attrs={"name": "keywords"})
  if keywords is None:
    keywords = soup.find("meta", attrs={"property": "og:keywords"})
  return extract_content(keywords)


async def fetch_data(url: str):
  html = await get_html(url)
  if html is None:
    return "获取数据失败: 网页内容为空"
  else:
    title = await get_title(html)
    summary = await get_summary(html)
    keywords = await get_keywords(html)
    return f"""标题：{title}
简介：{summary}
关键词：{keywords}"""
