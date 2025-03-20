import json

import aiohttp


async def trace_moe_util(data: bytes):
  url = "https://api.trace.moe/search?anilistInfo"
  headers = {"Content-Type": "image/jpeg"}

  async with aiohttp.ClientSession() as session:
    async with session.post(url, data=data, headers=headers) as response:
      # 获取并解析响应
      if response.status == 200:
        res = await response.json()
        return res

      else:
        return


async def trace_character_util(data: bytes, filename="test.jpg"):
  data2 = aiohttp.FormData()
  data2.add_field(
    "image",
    data,
    filename=filename,
  )
  # 发送请求
  model = "anime_model_lovelive"
  ai_detect = 0
  url = f"https://aiapiv2.animedb.cn/ai/api/detect?force_one=1&model={model}&ai_detect={ai_detect}"
  headers = {
    "User-Agent": (
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67"
    ),
  }
  async with aiohttp.ClientSession() as session:
    async with session.post(url=url, headers=headers, data=data2) as res:
      if res.status == 200:
        try:
          return await res.json()
        except aiohttp.ContentTypeError:
          # 如果JSON解析失败，尝试获取原始文本并将其解析为JSON
          text = await res.text()
          try:
            # 假设文本是JSON字符串，尝试解析
            json_content = json.loads(text)
            return json_content["data"]
          except json.JSONDecodeError:
            raise Exception(f"无法将响应转换为JSON，返回内容:\n{text}")
      else:
        # 处理其他状态码，获取错误信息
        error_message = await res.text()  # 获取错误信息
        raise Exception(f"请求失败，状态码: {res.status}, 错误信息: {error_message}")
