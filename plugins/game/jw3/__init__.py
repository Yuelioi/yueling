from nonebot import on_command
from nonebot.plugin import PluginMetadata

from core.deps import Args
from core.handler import register_handler
from core.http import get_client
from core.context import ToolContext

__plugin_meta__ = PluginMetadata(
  name="剑网三小工具",
  description="剑网三物价查询",
  usage="""物价 [商品名]""",
  extra={
    "group": "game",
    "commands": ["物价"],
    "tools": [{
      "name": "jw3_price",
      "description": "查询剑网三物品价格",
      "tags": ["game"],
      "examples": ["查物价 大橙武", "剑网三物价 xxx"],
      "parameters": {
        "keyword": {"type": "string", "description": "物品关键词"},
      },
      "handler": "jw3_tool_handler",
    }],
  },
)


jw3_price = on_command("物价")


URL_APPERANCE_SEARCH = "https://trade-api.seasunwbl.com/api/platform/setting/goods_appearance_name_search?game_id=jx3&keyword="
URL_PRICE = "https://trade-api.seasunwbl.com/m_api/buyer/goods/list"
# URL_APPERANCE = "https://trade-api.seasunwbl.com/m_api/platform/setting/goods_appearance_name_search"

params_price = {
  "goods_type": "3",
  "game": "jx3",
  "game_id": "jx3",
  "sort[price]": "1",
  "filter[state]": "0",
  "filter[appearance_type]": "",
  "filter[role_appearance]": "",
  "filter[price]": "0",
  "size": "10",
  "page": "1",
}

params_appearnce = {
  # "goods_type": "3",
  "game_id": "jx3",
  "keyword": "",
}


headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                   (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
  "Accept": "application/json",
}


async def get_price(keyword):
  """获取指定关键词的商品价格信息"""
  params_price_copy = params_price.copy()
  params_price_copy["keyword"] = keyword
  client = get_client()
  response = await client.get(URL_PRICE, params=params_price_copy, headers=headers)
  if response.status_code == 200:
    data = response.json()

    products = data["data"]["list"]
    if not products:
      return None

    msg = products[0]["info"] + "\n"
    return msg + "/".join(str(item["single_unit_price"] / 100) for item in products[:3])
  return None


async def appearance(keyword: str):
  """根据关键词搜索商品外观信息"""
  params_appearnce_copy = params_appearnce.copy()
  params_appearnce_copy["keyword"] = keyword
  client = get_client()
  response = await client.get(URL_APPERANCE_SEARCH, params=params_appearnce_copy, headers=headers)
  if response.status_code == 200:
    data = response.json()

    products = data["data"]["list"]
    if not products:
      return []
    return products[:10]
  return []


async def price(args=Args()):
  """主函数：查询商品价格，如果直接搜索无结果则通过外观搜索获取商品名称再查询"""
  keyword = "".join(args)

  # 如果直接搜索无结果，通过appearance搜索获取商品名称
  products = await appearance(keyword)
  if not products:
    direct_result = await get_price(keyword)
    if direct_result:
      return direct_result

  # 汇总结果
  summary_results = []

  for product in products:
    product_name = product["name"]
    price_info = await get_price(product_name)

    if price_info:
      summary_results.append(f"{price_info}\n")
    else:
      summary_results.append(f"{product['name']}: 暂无价格信息\n")

  if not summary_results:
    return "未找到相关商品价格信息"

  return "=" * 3 + " " + keyword + " " + "=" * 3 + "\n" + "\n".join(summary_results)


register_handler(jw3_price, price)


# ─── AI Tool 入口 ─────────────────────────────────────────


async def jw3_tool_handler(ctx: ToolContext, keyword: str) -> str:
  products = await appearance(keyword)
  if not products:
    direct = await get_price(keyword)
    return direct or f"未找到「{keyword}」"

  lines = [f"「{keyword}」物价:"]
  for product in products[:3]:
    info = await get_price(product["name"])
    lines.append(info or f"{product['name']}: 暂无")
  return "\n".join(lines)
