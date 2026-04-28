"""趣味 API 封装"""

import urllib.parse

from services.http_fetch import fetch_image, fetch_json, fetch_text


async def shadiao():
  res = await fetch_json("https://api.yujn.cn/api/shadiao.php")
  return res["title"], res["content"]


async def xiaoheizi():
  return await fetch_image("http://api.yujn.cn/api/cxk.php")


async def chat(msg: str):
  res = await fetch_text(f"https://api.yujn.cn/api/moli.php?msg={msg}")
  words = {"遇见": "月灵"}
  for v, k in words.items():
    res = res.replace(v, k)
  return res


async def chi():
  return await fetch_text("https://api.yujn.cn/api/chi.php")


async def chaijun():
  return await fetch_image("http://api.yujn.cn/api/chaijun.php")


async def fun_gif():
  return await fetch_image("http://api.yujn.cn/api/gif.php")


async def tiangou():
  return await fetch_text("http://api.yujn.cn/api/tiangou.php")


async def lvcha():
  return await fetch_text("http://api.yujn.cn/api/lvchayy.php")


async def shenhuifu():
  return await fetch_text("http://api.yujn.cn/api/shf.php")


async def kfc():
  return await fetch_text("http://api.yujn.cn/api/kfc.php")


async def read60s():
  return await fetch_image("http://api.yujn.cn/api/60SReadWorld.php")


async def trace(img):
  base_url = "https://api.trace.moe/search?cutBorders&anilistInfo&url={}"
  encoded_url = urllib.parse.quote_plus(img)
  full_url = base_url.format(encoded_url)
  return await fetch_json(full_url)


async def read60s_2():
  data = await fetch_json("https://api.2xb.cn/zaob")
  return await fetch_image(data["imageUrl"])
