"""HTML 解析工具"""

from bs4 import BeautifulSoup, NavigableString, Tag

from core.http import get_client


def _extract_content(node: Tag | NavigableString | None) -> str:
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


async def get_html(url: str) -> str | None:
  client = get_client()
  response = await client.get(url)
  if response.status_code == 200:
    return response.text
  return None


def get_title(html: str) -> str | None:
  soup = BeautifulSoup(html, "html.parser")
  return soup.title.string if soup.title else None


def get_summary(html: str) -> str:
  soup = BeautifulSoup(html, "html.parser")
  summary = soup.find("meta", attrs={"name": "description"})
  if summary is None:
    summary = soup.find("meta", attrs={"property": "og:description"})
  return _extract_content(summary)


def get_keywords(html: str) -> str:
  soup = BeautifulSoup(html, "html.parser")
  keywords = soup.find("meta", attrs={"name": "keywords"})
  if keywords is None:
    keywords = soup.find("meta", attrs={"property": "og:keywords"})
  return _extract_content(keywords)


async def fetch_page_data(url: str) -> str:
  html = await get_html(url)
  if html is None:
    return "获取数据失败: 网页内容为空"
  title = get_title(html)
  summary = get_summary(html)
  keywords = get_keywords(html)
  return f"标题：{title}\n简介：{summary}\n关键词：{keywords}"
