import re

import aiohttp
from bs4 import BeautifulSoup
from nonebot import require
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from nonebot_plugin_alconna import UniMsg, on_alconna
from nonebot_plugin_waiter import waiter

from common.Alc.Alc import msg
from common.config import config
from common.utils import text_to_image

"""
基于cookie验证 暂时不维护
"""

require("nonebot_plugin_waiter")
_zhihu = msg()

last_url = ""

zhihu = on_alconna(_zhihu)
# link_analysis = on_message()


async def zhihu_handler(url: str):
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": config.cookie.zhihu_cookies,
  }
  async with aiohttp.ClientSession() as session:
    async with session.get(url, headers=headers) as response:
      if response.status == 200:
        html = await response.text()
        soup = BeautifulSoup(html, "html.parser")

        title = "无标题"
        content = "无内容"
        if node := soup.select_one("head title"):
          title = node.get_text()
        if node := soup.select_one(".RichContent .RichText"):
          content = node.get_text()

        return {"标题": title, "内容": content[:100]}
      else:
        await zhihu.send("请回复验证码：")

        @waiter(["message"], keep_session=True)
        async def receive(msg: UniMsg):
          return msg

        async for res in receive(timeout=3):
          if not res:
            await zhihu.send("超时")
            return
          if str(res) == "123456":
            await zhihu.finish("验证成功")
            break
          await zhihu.send("验证失败，请重新输入：")
          continue


async def zhihuzhuanlan(url):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      html = await response.text()
      soup = BeautifulSoup(html, "html.parser")
      if (
        (post_title := soup.select_one(".Post-Title"))
        and (post_time := soup.select_one(".ContentItem-time"))
        and (meta_description := soup.find("meta", attrs={"name": "description"}))
      ):
        date_pattern = r"\d{4}-\d{2}-\d{2}"
        data_matches = re.findall(date_pattern, post_time.text.strip())

        texts = [
          f"标题: {post_title.text.strip()}",
          f"时间: {data_matches[0]}",
          f"概述: {meta_description.get('content')}",  # type: ignore
        ]

        img = text_to_image(texts)
        return MS.image(img) + MS.text(f"链接:{url}")
