"""
微博数据获取插件
fork from https://github.com/fllesser/nonebot-plugin-resolver2/blob/master/nonebot_plugin_resolver2/matchers/weibo.py
"""

import json
import math
import re

import aiohttp
from nonebot import logger
from nonebot_plugin_alconna import UniMessage

from common.utils.api import fetch_image_from_url
from plugins.group.file.utils import fetch_file_url

"""
https://weibo.com/1195908387/5125394590599698 not work
"""
from nonebot.adapters.onebot.v11 import MessageSegment

headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}


# 使用手机端 不再需要cookie
async def _create_weibo_cookies():
  data = {
    "cb": "visitor_gray_callback",
    "tid": "",
    "from": "weibo",
  }
  async with aiohttp.ClientSession() as session:
    async with session.post("https://passport.weibo.com/visitor/genvisitor2", headers=headers, data=data) as response:
      if response.status != 200:
        return None

      sub = json.loads(re.findall(r"({.*})", await response.text())[0])["data"]["sub"]
      return {"Cookie": f"SUB={sub}"}


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base62_encode(number):
  """将数字转换为 base62 编码"""
  if number == 0:
    return "0"

  result = ""
  while number > 0:
    result = ALPHABET[number % 62] + result
    number //= 62

  return result


def mid2id(mid):
  mid = str(mid)[::-1]  # 反转输入字符串
  size = math.ceil(len(mid) / 7)  # 计算每个块的大小
  result = []

  for i in range(size):
    # 对每个块进行处理并反转
    s = mid[i * 7 : (i + 1) * 7][::-1]
    # 将字符串转为整数后进行 base62 编码
    s = base62_encode(int(s))
    # 如果不是最后一个块并且长度不足4位，进行左侧补零操作
    if i < size - 1 and len(s) < 4:
      s = "0" * (4 - len(s)) + s
    result.append(s)

  result.reverse()  # 反转结果数组
  return "".join(result)  # 将结果数组连接成字符串


def extract_mid(url):
  """提取微博 id"""
  weibo_id = None

  if match := re.search(r"m\.weibo\.cn(?:/detail|/status)?/([A-Za-z\d]+)", url):
    weibo_id = match.group(1)
  # https://weibo.com/tv/show/1034:5007449447661594?mid=5007452630158934
  elif match := re.search(r"mid=([A-Za-z\d]+)", url):
    weibo_id = mid2id(match.group(1))
  # https://weibo.com/1707895270/5006106478773472
  elif match := re.search(r"(?<=weibo.com/)[A-Za-z\d]+/([A-Za-z\d]+)", url):
    weibo_id = match.group(1)

  return weibo_id


async def weibo(url: str):
  weibo_id = extract_mid(url)
  if not weibo_id:
    return
  url = f"https://weibo.com/ajax/statuses/show?id={weibo_id}&locale=zh-CN&isGetLongText=true"
  headers = await _create_weibo_cookies()
  if not headers:
    return

  async with aiohttp.ClientSession() as session:
    async with session.get(url, headers=headers) as response:
      if response.status != 200:
        return

      data = await response.json()
      return parse(data, headers)


def parse(data, headers=None):
  title = data["text_raw"].strip().split("\n")[0]
  page_info = data.get("page_info", {})

  if page_info and page_info.get("object_type") == "video":
    video = page_info.get("media_info", {})
    if video:
      media = video.get("stream_url")  # stream_url / stream_url_hd / h5_url
      if media:
        return UniMessage.video(url=media)

  elif data.get("pic_infos", {}):
    msgs = UniMessage.text(f"标题：{title}\n")
    pic_infos = data.get("pic_infos", {})
    if pic_infos:
      for pic_info in pic_infos.values():
        img = pic_info.get("thumbnail")  # thumbnail
        msgs += UniMessage.image(url=img["url"])

    return msgs


# 貌似不行
async def _weibo(url: str):
  weibo_id = extract_mid(url)
  if not weibo_id:
    return
  logger.info(f"获取微博：{weibo_id}")

  url = f"https://m.weibo.cn/statuses/show?id={weibo_id}"
  async with aiohttp.ClientSession() as session:
    async with session.get(url, headers=headers) as response:
      if response.status != 200:
        return

      data = await response.json()
      return parse(data)
