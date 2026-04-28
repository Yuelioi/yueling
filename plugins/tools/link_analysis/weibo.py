"""
微博数据获取插件
fork from https://github.com/fllesser/nonebot-plugin-resolver2/blob/master/nonebot_plugin_resolver2/matchers/weibo.py
"""

import json
import math
import re


from core.http import get_client, USER_AGENT


headers = {"User-Agent": USER_AGENT}


async def _create_weibo_cookies():
  data = {
    "cb": "visitor_gray_callback",
    "tid": "",
    "from": "weibo",
  }
  client = get_client()
  response = await client.post("https://passport.weibo.com/visitor/genvisitor2", headers=headers, data=data)
  if response.status_code != 200:
    return None

  sub = json.loads(re.findall(r"({.*})", response.text)[0])["data"]["sub"]
  return {"Cookie": f"SUB={sub}"}


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base62_encode(number):
  if number == 0:
    return "0"
  result = ""
  while number > 0:
    result = ALPHABET[number % 62] + result
    number //= 62
  return result


def mid2id(mid):
  mid = str(mid)[::-1]
  size = math.ceil(len(mid) / 7)
  result = []

  for i in range(size):
    s = mid[i * 7 : (i + 1) * 7][::-1]
    s = base62_encode(int(s))
    if i < size - 1 and len(s) < 4:
      s = "0" * (4 - len(s)) + s
    result.append(s)

  result.reverse()
  return "".join(result)


def extract_mid(url):
  weibo_id = None

  if match := re.search(r"m\.weibo\.cn(?:/detail|/status)?/([A-Za-z\d]+)", url):
    weibo_id = match.group(1)
  elif match := re.search(r"mid=([A-Za-z\d]+)", url):
    weibo_id = mid2id(match.group(1))
  elif match := re.search(r"(?<=weibo.com/)[A-Za-z\d]+/([A-Za-z\d]+)", url):
    weibo_id = match.group(1)

  return weibo_id


async def weibo(url: str):
  weibo_id = extract_mid(url)
  if not weibo_id:
    return
  api_url = f"https://weibo.com/ajax/statuses/show?id={weibo_id}&locale=zh-CN&isGetLongText=true"
  cookie_headers = await _create_weibo_cookies()
  if not cookie_headers:
    return

  client = get_client()
  response = await client.get(api_url, headers=cookie_headers)
  if response.status_code != 200:
    return

  data = response.json()
  return parse(data)


def parse(data, headers=None):
  title = data["text_raw"].strip().split("\n")[0]
  return f"微博: {title}"
