"""AI 内置工具 — 联网能力（搜索、天气、机票、车票）"""

from urllib.parse import quote_plus

from ai.registry import ai_tool
from core.context import ToolContext
from core.http import get_client, get_proxy_client


@ai_tool(
  description="联网搜索，返回摘要结果",
  tags=["search", "web"],
  examples=["帮我搜一下xxx", "搜索最新的xxx新闻", "查一下xxx是什么意思"],
  triggers=["搜", "搜索"],
  patterns=[r"帮我搜.+", r"查一下.+"],
  semantic_slots=["联网搜索", "搜一下", "查询"],
)
async def web_search(ctx: ToolContext, query: str) -> str:
  """联网搜索，返回摘要结果

  Args:
    query: 搜索关键词
  """
  try:
    async with get_proxy_client() as client:
      url = f"https://www.bing.com/search?q={quote_plus(query)}&setlang=zh-CN"
      resp = await client.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
      })
      if resp.status_code != 200:
        return f"搜索失败(HTTP {resp.status_code})"

      from bs4 import BeautifulSoup
      soup = BeautifulSoup(resp.text, "html.parser")
      results = []

      for item in soup.select(".b_algo")[:5]:
        title_el = item.select_one("h2")
        snippet_el = item.select_one(".b_caption p") or item.select_one("p")
        title = title_el.get_text(strip=True) if title_el else ""
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
        if title or snippet:
          results.append(f"【{title}】{snippet}" if title else snippet)

      if not results:
        return f"未找到'{query}'的相关结果"
      return "\n".join(results)
  except Exception as e:
    return f"搜索失败: {e}"


@ai_tool(
  description="查询城市天气",
  tags=["info", "web"],
  examples=["今天天气怎么样", "北京明天天气", "上海这周天气预报"],
  triggers=["天气", "气温"],
  semantic_slots=["天气预报", "下雨", "温度"],
)
async def get_weather(ctx: ToolContext, city: str = "") -> str:
  """查询城市天气

  Args:
    city: 城市名(中文)，不填则用IP定位
  """
  try:
    client = get_client()
    if city:
      url = f"https://wttr.in/{quote_plus(city)}?format=j1&lang=zh"
    else:
      url = "https://wttr.in/?format=j1&lang=zh"
    resp = await client.get(url, headers={"Accept-Language": "zh-CN"})
    if resp.status_code != 200:
      return f"天气查询失败(HTTP {resp.status_code})"
    data = resp.json()

    current = data.get("current_condition", [{}])[0]
    area = data.get("nearest_area", [{}])[0]
    location = area.get("areaName", [{}])[0].get("value", city or "当前位置")

    desc = current.get("lang_zh", [{}])[0].get("value", "") if current.get("lang_zh") else current.get("weatherDesc", [{}])[0].get("value", "")
    temp = current.get("temp_C", "?")
    feels = current.get("FeelsLikeC", "?")
    humidity = current.get("humidity", "?")

    lines = [
      f"{location}: {desc} {temp}°C (体感{feels}°C) 湿度{humidity}%",
    ]

    forecasts = data.get("weather", [])[:3]
    for day in forecasts:
      date = day.get("date", "")
      max_t = day.get("maxtempC", "?")
      min_t = day.get("mintempC", "?")
      hourly = day.get("hourly", [{}])
      desc_f = ""
      for h in hourly:
        if h.get("lang_zh"):
          desc_f = h["lang_zh"][0].get("value", "")
          break
      lines.append(f"{date}: {min_t}~{max_t}°C {desc_f}")

    return "\n".join(lines)
  except Exception as e:
    return f"天气查询失败: {e}"


@ai_tool(
  description="查询机票/航班信息",
  tags=["search", "travel"],
  examples=["北京到上海的机票", "查一下明天飞广州的航班", "机票查询"],
  triggers=["机票", "航班"],
  patterns=[r".+到.+机票"],
  semantic_slots=["飞机票", "航班查询"],
)
async def search_flights(ctx: ToolContext, departure: str, arrival: str, date: str = "") -> str:
  """查询机票/航班信息

  Args:
    departure: 出发城市
    arrival: 到达城市
    date: 出发日期(YYYY-MM-DD)，不填=今天
  """
  query = f"{departure}到{arrival}机票 {date}".strip()
  return await web_search(ctx, query)


@ai_tool(
  description="查询火车票/高铁票信息",
  tags=["search", "travel"],
  examples=["北京到上海的火车票", "查一下高铁票", "明天去南京的车票"],
  triggers=["火车", "高铁", "车票"],
  patterns=[r".+到.+火车", r".+到.+高铁"],
  semantic_slots=["火车票", "高铁票"],
)
async def search_trains(ctx: ToolContext, departure: str, arrival: str, date: str = "") -> str:
  """查询火车票/高铁票信息

  Args:
    departure: 出发城市/车站
    arrival: 到达城市/车站
    date: 出发日期(YYYY-MM-DD)，不填=今天
  """
  query = f"{departure}到{arrival}高铁火车票 {date}".strip()
  return await web_search(ctx, query)
