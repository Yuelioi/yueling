"""AI 内置工具 — 社交互动（好感排行、匿名留言、星座运势、成语接龙）"""

import random

from ai.llm import llm_complete
from ai.registry import tool
from core import store
from core.context import ToolContext
from core.http import get_client


@tool(
  tags=["context", "group"],
  examples=["好感排行", "谁和月灵关系最好", "好感度排行榜"],
)
async def affinity_ranking(ctx: ToolContext) -> str:
  """显示当前群的好感度排行榜"""
  try:
    members = await ctx.bot.get_group_member_list(group_id=ctx.group_id)
    member_map = {str(m["user_id"]): m.get("card") or m.get("nickname", "?") for m in members}
  except Exception:
    member_map = {}

  all_prefs = store.user_prefs.all()
  group_prefs = []
  for uid, like in all_prefs.items():
    if uid in member_map:
      group_prefs.append((member_map[uid], like))

  if not group_prefs:
    return "暂无好感数据"

  group_prefs.sort(key=lambda x: x[1], reverse=True)
  lines = ["好感度排行:"]
  medals = ["🥇", "🥈", "🥉"]
  for i, (name, like) in enumerate(group_prefs[:10]):
    prefix = medals[i] if i < 3 else f"{i+1}."
    lines.append(f"{prefix} {name}: {like}")
  return "\n".join(lines)


@tool(
  tags=["fun"],
  examples=["帮我匿名说一句话", "匿名吐槽", "匿名表白"],
)
async def anonymous_message(ctx: ToolContext, message: str) -> str:
  """以月灵的名义转发一条匿名消息到群里

  Args:
    message: 要匿名发送的内容
  """
  if len(message) > 200:
    return "消息太长了，200字以内"
  if len(message) < 2:
    return "消息太短了"

  prefixes = ["有人想说:", "匿名消息:", "有位群友想说:", "收到一条匿名消息:"]
  text = f"💌 {random.choice(prefixes)}\n{message}"
  try:
    await ctx.bot.send_group_msg(group_id=ctx.group_id, message=text)
    return "已匿名发送"
  except Exception:
    return "发送失败"


@tool(
  tags=["fun", "info"],
  examples=["白羊座今天运势", "双子座运势", "天蝎座今天怎么样"],
)
async def horoscope(ctx: ToolContext, sign: str) -> str:
  """查询星座今日运势

  Args:
    sign: 星座名(白羊座/金牛座/双子座/巨蟹座/狮子座/处女座/天秤座/天蝎座/射手座/摩羯座/水瓶座/双鱼座)
  """
  sign_map = {
    "白羊座": "aries", "金牛座": "taurus", "双子座": "gemini",
    "巨蟹座": "cancer", "狮子座": "leo", "处女座": "virgo",
    "天秤座": "libra", "天蝎座": "scorpio", "射手座": "sagittarius",
    "摩羯座": "capricorn", "水瓶座": "aquarius", "双鱼座": "pisces",
  }
  sign = sign.strip()
  if sign not in sign_map:
    for k in sign_map:
      if sign in k or k.startswith(sign):
        sign = k
        break
  if sign not in sign_map:
    return f"不认识的星座'{sign}'，支持: {', '.join(sign_map.keys())}"

  try:
    client = get_client()
    resp = await client.get(
      f"https://api.vvhan.com/api/horoscope?type={sign_map[sign]}&time=today",
      timeout=10,
    )
    if resp.status_code != 200:
      return "查询失败"
    data = resp.json()
    if not data.get("success"):
      return "查询失败"
    d = data.get("data", {})
    lines = [f"⭐ {sign}今日运势"]
    if d.get("shortcomment"):
      lines.append(d["shortcomment"])
    fortune_list = d.get("fortune", [])
    for item in fortune_list[:4]:
      lines.append(f"{item.get('name', '')}: {item.get('star', '')} {item.get('text', '')}")
    lucky = d.get("luckynum", "")
    color = d.get("luckycolor", "")
    if lucky or color:
      lines.append(f"幸运数字: {lucky}  幸运颜色: {color}")
    return "\n".join(lines)
  except Exception as e:
    return f"查询失败: {e}"


@tool(
  tags=["fun", "language"],
  examples=["成语接龙 一帆风顺", "接龙", "来玩成语接龙"],
)
async def idiom_chain(ctx: ToolContext, idiom: str) -> str:
  """成语接龙，给出一个成语，月灵接下一个

  Args:
    idiom: 上一个成语
  """
  idiom = idiom.strip()
  if len(idiom) < 3:
    return "请给一个成语（至少3个字）"
  try:
    reply = await llm_complete(
      "你是成语接龙高手。规则：用对方成语的最后一个字（同音也可以）作为开头，接一个新成语。"
      "只回复一个成语（4个字），不要加任何解释。如果实在接不上就说"接不上了，你赢了！"",
      idiom,
      temperature=0.8,
      max_tokens=20,
    )
    return reply.strip()
  except Exception:
    return "接不上了，你赢了！"


@tool(
  tags=["fun"],
  examples=["今天适合做什么", "今天老黄历", "宜忌查询"],
)
async def daily_fortune(ctx: ToolContext) -> str:
  """查看今日宜忌（老黄历风格随机生成）"""
  good_things = [
    "摸鱼", "写代码", "吃火锅", "打游戏", "看番", "逛街", "告白", "加班",
    "学习", "健身", "睡懒觉", "出门旅行", "网购", "做饭", "追剧", "打扫房间",
    "约朋友", "喝奶茶", "拍照", "画画", "弹琴", "唱歌", "写日记",
  ]
  bad_things = [
    "熬夜", "吵架", "剁手", "迟到", "说谎", "偷懒", "发脾气", "暴饮暴食",
    "翘课", "玩手机到半夜", "不吃早饭", "忘带钥匙", "踩水坑", "忘记保存",
    "开黑连败", "修电脑", "相亲", "体检", "考试", "面试",
  ]
  yi = random.sample(good_things, 3)
  ji = random.sample(bad_things, 3)
  luck = random.choice(["大吉", "中吉", "小吉", "吉", "末吉", "凶", "小凶"])
  return (
    f"📅 今日运势: {luck}\n"
    f"宜: {'、'.join(yi)}\n"
    f"忌: {'、'.join(ji)}"
  )
