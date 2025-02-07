from common.utils.api import get_html, get_summary, get_title

# https://zhuanlan.zhihu.com/p/663061200


async def zhihuzhuanlan(url: str):
  url = url.replace("zhihu", "fxzhihu")
  html = await get_html(url)
  if html is None:
    return

  title = await get_title(html)
  summary = await get_summary(html)

  if len(summary) > 75:
    summary = summary[:75] + "..."

  return f"标题：{title}\n摘要：{summary}"
