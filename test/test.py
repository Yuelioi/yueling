import asyncio

import aiohttp

# 目标URL
URL = "https://trade-api.seasunwbl.com/m_api/buyer/goods/list"

# 请求参数
params = {
  "goods_type": "3",
  "game": "jx3",
  "keyword": "灰发星虹",
  "game_id": "jx3",
  "sort[price]": "1",
  "filter[state]": "2",
  "filter[appearance_type]": "",
  "filter[price]": "0",
  "size": "10",
  "page": "1",
}

# 请求头（可选，但有时能避免被识别为爬虫）
headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                   (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
  "Accept": "application/json",
}


async def fetch_goods():
  async with aiohttp.ClientSession() as session:
    async with session.get(URL, params=params, headers=headers) as response:
      if response.status == 200:
        data = await response.json()
        first = data["data"]["list"][0]

        print(first["info"])
        print(first["single_unit_price"])


if __name__ == "__main__":
  asyncio.run(fetch_goods())
