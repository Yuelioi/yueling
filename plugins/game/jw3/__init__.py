import aiohttp
from nonebot import on_command
from nonebot.plugin import PluginMetadata

from common.base.Depends import Args
from common.base.Handle import register_handler

__plugin_meta__ = PluginMetadata(
  name="剑网三小工具",
  description="剑网三物价查询",
  usage="""外观/物价 [商品名]""",
  extra={"group": "game", "commands": ["外观", "物价"]},
)


jw3_price = on_command("物价")
jw3_apperance = on_command("外观")

URL_PRICE = "https://trade-api.seasunwbl.com/m_api/buyer/goods/list"
URL_APPERANCE = "https://trade-api.seasunwbl.com/m_api/platform/setting/goods_appearance_name_search"

params_price = {
  "goods_type": "3",
  "game": "jx3",
  "game_id": "jx3",
  "sort[price]": "1",
  "filter[state]": "2",
  "filter[appearance_type]": "",
  "filter[price]": "0",
  "size": "10",
  "page": "1",
}

params_appearnce = {
  "goods_type": "3",
  "game_id": "jx3",
}


headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                   (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
  "Accept": "application/json",
}


async def price(args=Args()):
  keyword = "".join(args)
  params_price["keyword"] = keyword

  async with aiohttp.ClientSession() as session:
    async with session.get(URL_PRICE, params=params_price, headers=headers) as response:
      if response.status == 200:
        data = await response.json()

        products = data["data"]["list"]
        if not products:
          return "请指定更准确的名称喔"

        msg = products[0]["info"] + "\n"

        return msg + "/".join(str(item["single_unit_price"] / 100) for item in products[:3])


async def apperance(args=Args()):
  keyword = "".join(args)
  params_appearnce["keyword"] = keyword

  async with aiohttp.ClientSession() as session:
    async with session.get(URL_APPERANCE, params=params_appearnce, headers=headers) as response:
      if response.status == 200:
        data = await response.json()

        products = data["data"]["list"]
        if not products:
          return "请指定更准确的名称喔"

        return "\n".join(f"{index + 1}:{item['name']} 类型:{item['category']}" for index, item in enumerate(products[:20]))


register_handler(jw3_price, price)
register_handler(jw3_apperance, apperance)
