import asyncio
import re
from typing import cast

from bs4 import BeautifulSoup, Tag

from common.utils.api import fetch_text_from_url


async def get_download_link(url):
  if content := await fetch_text_from_url(url):
    soup = BeautifulSoup(content, "html.parser")

    if baidu_link := soup.find("a", string=re.compile("百度网盘")):
      baidu_link = cast(Tag, baidu_link)
      return baidu_link["href"]


async def search_ae_plugin(arg: str):
  if content := await fetch_text_from_url(f"https://www.lookae.com/?s={arg}"):
    soup = BeautifulSoup(content, "html.parser")

    articles = soup.find_all("article")

    tasks = []
    titles = []
    source_webs = []
    for article in articles[:3]:
      title = article.find("h2").text
      link = article.find("a")["href"]
      source_webs.append(link)

      titles.append(title)
      tasks.append(get_download_link(link))

    baidu_links = await asyncio.gather(*tasks)

    result = ""
    for index, title in enumerate(titles):
      result += f"{index+1}.{title}\n"
      result += f"网站: {source_webs[index]}\n"
      result += f"百度网盘: {baidu_links[index]}\n"
      result += "\n"

    if not result:
      return f"搜索不到,请访问原网站 https://www.lookae.com/?s={arg}"
    return result.strip()
