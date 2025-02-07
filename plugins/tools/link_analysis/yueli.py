import aiohttp
from bs4 import BeautifulSoup
from nonebot.adapters.onebot.v11 import MessageSegment as MS


async def yuelili(url):
  async with aiohttp.ClientSession() as session:
    async with session.get(url, ssl=False) as response:
      html = await response.text()
      soup = BeautifulSoup(html, "html.parser")
      meta_tags = soup.find_all("meta")
      image = title = url = description = ""
      for meta in meta_tags:
        if "property" in meta.attrs:
          if meta.attrs["property"] == "og:image":
            image = meta.attrs["content"]
          if meta.attrs["property"] == "og:title":
            title = meta.attrs["content"]
          if meta.attrs["property"] == "og:url":
            url = meta.attrs["content"]

        if "name" in meta.attrs:
          if meta.attrs["name"] == "description":
            description = meta.attrs["content"]
      return MS.image(image) + MS.text(f"标题: { title }\n简介: { description}\n链接: { url }")
