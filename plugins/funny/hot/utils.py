import aiohttp
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from common.biz import user_agent

router = APIRouter()


async def bilibili():
  async with aiohttp.ClientSession() as session:
    async with session.get(
      "https://app.bilibili.com/x/topic/web/dynamic/rcmd?source=Web&page_size=10", headers={"User-Agent": user_agent}
    ) as response:
      if response.status == 200:
        topic_items = (await response.json())["data"]["topic_items"]
        res = [item["name"] for item in topic_items]
        return [f"{index + 1}. {d}" for index, d in enumerate(res)]
      return []


async def zhihu():
  async with aiohttp.ClientSession() as session:
    async with session.get("https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true") as response:
      if response.status == 200:
        topic_items = (await response.json())["data"][:10]
        res = [item["target"]["title"] for item in topic_items]
        return [f"{index + 1}. {d}" for index, d in enumerate(res)]
      return []


async def weibo():
  async with aiohttp.ClientSession() as session:
    async with session.get("https://weibo.com/ajax/side/hotSearch") as response:
      if response.status == 200:
        topic_items = (await response.json())["data"]["realtime"][:10]
        res = [item["word"] for item in topic_items]
        return [f"{index + 1}. {d}" for index, d in enumerate(res)]
      return []


async def baidu():
  async with aiohttp.ClientSession() as session:
    async with session.get("https://top.baidu.com/api/board?platform=wise&tab=realtime") as response:
      if response.status == 200:
        topic_items = (await response.json())["data"]["cards"][0]["content"][:10]
        res = [item["query"] for item in topic_items]
        return [f"{index + 1}. {d}" for index, d in enumerate(res)]
      return []
