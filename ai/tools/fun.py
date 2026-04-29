"""AI 内置工具 — 趣味工具（缩写解码、诗词、鸡汤、热评）"""

from ai.registry import ai_tool
from core.context import ToolContext
from core.http import get_client


@ai_tool(
  description="解码拼音缩写/网络黑话，如yyds、xswl、awsl等",
  tags=["language", "info"],
  examples=["yyds是什么意思", "xswl什么意思", "能不能好好说话"],
  triggers=["缩写", "什么意思"],
  patterns=[r"\w{2,6}(是什么|啥意思)"],
  semantic_slots=["网络黑话", "拼音缩写", "yyds"],
)
async def decode_abbreviation(ctx: ToolContext, text: str) -> str:
  """解码拼音缩写/网络黑话，如yyds、xswl、awsl等

  Args:
    text: 要解码的缩写
  """
  try:
    client = get_client()
    resp = await client.post(
      "https://lab.magiconch.com/api/nbnhhsh/guess",
      json={"text": text.strip().lower()},
      timeout=10,
    )
    if resp.status_code != 200:
      return "查询失败"
    data = resp.json()
    if not data:
      return f"没有找到'{text}'的含义"
    results = []
    for item in data:
      name = item.get("name", "")
      trans = item.get("trans", []) or item.get("inputting", [])
      if trans:
        results.append(f"{name}: {', '.join(trans[:5])}")
    return "\n".join(results) if results else f"没有找到'{text}'的含义"
  except Exception as e:
    return f"查询失败: {e}"


@ai_tool(
  description="获取随机古诗词、心灵鸡汤或网易云音乐热评",
  tags=["fun"],
  examples=["来首诗", "来碗鸡汤", "随机一首古诗", "网易云热评"],
  triggers=["诗", "鸡汤", "热评"],
  patterns=[r"来(首|碗|条).+"],
  semantic_slots=["古诗词", "心灵鸡汤", "网易云"],
)
async def get_inspiration(ctx: ToolContext, category: str = "poetry") -> str:
  """获取随机古诗词、心灵鸡汤或网易云音乐热评

  Args:
    category: 类型(poetry/soup/comment)
  """
  try:
    client = get_client()
    if category == "poetry":
      resp = await client.get("https://v1.jinrishici.com/all.json", timeout=10)
      if resp.status_code == 200:
        data = resp.json()
        return f"「{data.get('content', '')}」\n—— {data.get('author', '')}《{data.get('origin', '')}》"
    elif category == "comment":
      resp = await client.get("https://api.vvhan.com/api/ian/rand?type=json", timeout=10)
      if resp.status_code == 200:
        data = resp.json()
        if data.get("success"):
          return data.get("data", {}).get("content", "获取失败")
    # soup fallback 或默认
    resp = await client.get("https://api.vvhan.com/api/ian/rand?type=json", timeout=10)
    if resp.status_code == 200:
      data = resp.json()
      if data.get("success"):
        return data.get("data", {}).get("content", "获取失败")
    return "获取失败"
  except Exception as e:
    return f"获取失败: {e}"


@ai_tool(
  description="查询当前Epic Games商店的免费游戏",
  tags=["info"],
  examples=["今天Epic有什么免费游戏", "Epic免费", "白嫖游戏"],
  triggers=["Epic", "免费游戏"],
  semantic_slots=["白嫖游戏", "Epic免费"],
)
async def epic_free_games(ctx: ToolContext) -> str:
  """查询当前Epic Games商店的免费游戏"""
  try:
    client = get_client()
    resp = await client.get(
      "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-CN&country=CN",
      timeout=15,
    )
    if resp.status_code != 200:
      return "查询失败"
    data = resp.json()
    elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
    free_games = []
    for game in elements:
      title = game.get("title", "")
      promotions = game.get("promotions")
      if not promotions:
        continue
      offers = promotions.get("promotionalOffers", [])
      if offers:
        for offer_group in offers:
          for offer in offer_group.get("promotionalOffers", []):
            if offer.get("discountSetting", {}).get("discountPercentage") == 0:
              desc = game.get("description", "")[:60]
              free_games.append(f"🎮 {title}\n   {desc}")
    if not free_games:
      return "当前没有免费游戏，请关注后续活动"
    return "Epic免费游戏:\n" + "\n".join(free_games)
  except Exception as e:
    return f"查询失败: {e}"
