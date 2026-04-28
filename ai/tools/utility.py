"""AI 内置工具 — 实用工具（日期计算、IP查询、随机人设、选择困难症）"""

import random
from datetime import datetime

from ai.llm import llm_complete
from ai.registry import tool
from core.context import ToolContext
from core.http import get_client


@tool(
  tags=["math", "info"],
  examples=["距离过年还有多少天", "100天后是几号", "2024年10月1日是星期几"],
)
async def date_calc(ctx: ToolContext, query: str) -> str:
  """日期计算：倒计时、推算日期、星期查询

  Args:
    query: 日期相关问题（如"距离2025-01-01还有多少天"或"30天后是几号"）
  """
  now = datetime.now()
  try:
    return await llm_complete(
      f"你是日期计算器。当前时间: {now.strftime('%Y-%m-%d %H:%M %A')}。直接回答日期计算结果，一句话，不要废话。",
      query,
      temperature=0.0,
      max_tokens=100,
      fallback="计算失败",
    )
  except Exception as e:
    return f"计算失败: {e}"


@tool(
  tags=["info"],
  examples=["查一下这个IP是哪里的", "114.514.0.1在哪", "ip归属地"],
)
async def ip_lookup(ctx: ToolContext, ip: str) -> str:
  """查询IP地址的归属地信息

  Args:
    ip: IP地址
  """
  try:
    client = get_client()
    resp = await client.get(f"https://whois.pconline.com.cn/ipJson.jsp?ip={ip}&json=true", timeout=10)
    if resp.status_code != 200:
      return "查询失败"
    data = resp.json()
    addr = data.get("addr", "未知")
    return f"IP {ip} → {addr}"
  except Exception as e:
    return f"查询失败: {e}"


@tool(
  tags=["fun"],
  examples=["帮我生成一个随机人设", "随机人设", "来个角色设定"],
)
async def random_persona(ctx: ToolContext) -> str:
  """生成一个随机虚拟人设"""
  names = ["苍月", "白夜", "赤羽", "千织", "幽兰", "星河", "雪见", "墨染", "清浅", "夜阑"]
  races = ["人类", "精灵", "龙族后裔", "半神", "机械生命", "吸血鬼", "狐妖", "天使", "恶魔", "人鱼"]
  jobs = ["剑士", "法师", "盗贼", "吟游诗人", "炼金术士", "赏金猎人", "占星师", "驯兽师", "咒术师", "铸甲师"]
  traits = ["沉默寡言但内心温柔", "话痨且社牛", "傲娇毒舌", "天然呆", "中二病晚期", "老好人", "腹黑", "怕生但战斗力爆表", "吃货", "路痴"]
  weapons = ["双刃剑", "魔法书", "匕首", "竖琴", "炼金壶", "双枪", "星盘", "鞭子", "咒符", "盾牌"]
  likes = ["猫", "甜食", "下雨天", "古书", "星空", "酒", "睡觉", "打架", "收集宝石", "旅行"]

  return (
    f"姓名: {random.choice(names)}\n"
    f"种族: {random.choice(races)}\n"
    f"职业: {random.choice(jobs)}\n"
    f"性格: {random.choice(traits)}\n"
    f"武器: {random.choice(weapons)}\n"
    f"喜好: {random.choice(likes)}\n"
    f"战力: {random.randint(1000, 99999)}"
  )


@tool(
  tags=["fun"],
  examples=["帮我做个决定", "选择困难症", "帮我选A还是B还是C"],
)
async def make_decision(ctx: ToolContext, options: str) -> str:
  """帮用户做选择，给出分析和建议（选择困难症拯救者）

  Args:
    options: 用空格或逗号分隔的选项
  """
  items = [o.strip() for o in options.replace(",", " ").replace("，", " ").split() if o.strip()]
  if len(items) < 2:
    return "至少给我两个选项啊！"
  if len(items) > 10:
    return "选项太多了，最多10个"

  chosen = random.choice(items)
  reasons = [
    "命运的齿轮如此转动",
    "月灵掐指一算",
    "直觉告诉我",
    "抛硬币的结果",
    "量子力学的选择",
    "塔罗牌指引",
    "第六感",
    "风水学分析后",
  ]
  return f"在 {' / '.join(items)} 中...\n{random.choice(reasons)}，选「{chosen}」！"
