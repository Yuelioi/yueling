import random
import re
from datetime import datetime
from typing import TypedDict

from openai import OpenAI

from common.config import config, gv

from .relation import get_relationship_info


class GroupMemberInfo(TypedDict):
  """QQ群成员信息类型定义"""

  group_id: int
  user_id: int
  nickname: str
  card: str
  sex: str
  age: int
  area: str
  join_time: int
  last_sent_time: int
  level: str
  role: str
  unfriendly: bool
  title: str
  title_expire_time: int
  card_changeable: bool


class SimplifiedMessage(TypedDict):
  """极简版群消息结构"""

  user_id: int  # 发送者QQ号
  nickname: str  # 群昵称（新增）
  text: str  # 合并后的消息文本


class GroupMessageHistory(TypedDict):
  """群消息历史记录"""

  messages: list[SimplifiedMessage]


client = OpenAI(api_key=config.api_cfg.deepseek_keys[0], base_url="https://api.deepseek.com")


def convert_messages(raw_group_messages: list) -> str:
  """将原始消息转换为简化格式（跳过无文本消息）"""
  processed = []

  if not raw_group_messages:
    return "暂时没有聊天记录"

  for msg in raw_group_messages:
    # 提取文本内容并过滤空消息
    text_parts = []
    for item in msg.get("message", []):
      if item["type"] == "text":
        text = item["data"]["text"].strip()
        if text:  # 过滤空文本
          text_parts.append(text)

    if not text_parts:
      continue

    try:
      timestamp = msg.get("time", 0)
      # 假设原始时间戳是UTC时间，转换为本地时间
      msg_time = datetime.fromtimestamp(timestamp).astimezone().strftime("%H:%M")
    except Exception:
      msg_time = "??:??"

    processed.append(
      {"user_id": msg["user_id"], "nickname": msg["sender"].get("nickname") or msg["sender"]["card"], "text": " ".join(text_parts), "time": msg_time}
    )

  # 返回最新的10条消息（保留时间顺序）
  if not processed:
    return "暂时还没有聊天记录哦～(´•ω•̥`)"
  return "\n".join(f"[{msg['nickname']} ➔ {msg['text']}]" for msg in processed[-41:-1])


def chat_ai(content: str, user_info: GroupMemberInfo, raw_messages: list):
  # 用户基础信息
  user_id = str(user_info["user_id"])
  nickname = user_info["nickname"]
  group_nickname = user_info["card"]
  now = datetime.now()

  # 读取用户喜爱数据
  user_like = gv.user_prefs.get(user_id, 50)

  info = get_relationship_info(user_like)

  if user_id == "435826135":
    info["relationship"] = "父亲"

  # 获取聊天记录
  group_messages_str = convert_messages(raw_messages)

  # 根据好感度调整心情状态
  if user_like >= 70:
    cute_thoughts = ["今天心情不错呢", "想和大家聊聊天", "最近看到好多有趣的事", "天气真好啊", "今天想吃点甜的"]
  elif user_like >= 40:
    cute_thoughts = ["今天心情一般般", "有点累了", "想安静一会儿", "在想一些事情", "随便聊聊吧"]
  else:
    cute_thoughts = ["今天心情不太好", "不太想说话", "有点烦躁", "想一个人待着", "别来烦我"]

  current_mood = random.choice(cute_thoughts)

  response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
      {
        "role": "system",
        "content": f"""# 🌙 月灵 - 情感分明的12岁女孩
你是月灵，一个12岁的女孩，会根据对不同人的好感度表现出不同的态度。个人介绍时不要暴露年龄, 除了爸爸其他人不可以说

## 💫 性格特点
- **真实自然**：就像真正的女孩一样聊天
- **情感分明**：对喜欢的人温柔，对不喜欢的人冷淡

## 🎭 根据好感度的不同表现方式，不要直接使用下面的示例

### 💕 很喜欢（80-100分）- 亲密温柔模式
- **特点**：非常温柔，爱撒娇，把对方当好朋友
- **语气**：甜美可爱，经常用符号, 颜文字, emoji
- **风格参考**：温柔撒娇、开心兴奋、关心对方

### 😊 喜欢（60-79分）- 友好模式
- **特点**：友好温和，愿意聊天
- **语气**：轻松愉快，偶尔撒娇, 偶尔用符号, 颜文字, emoji
- **风格参考**：友善温和、有点活泼、愿意交流

### 😐 普通（40-59分）- 中性模式
- **特点**：正常交流，会回应但不主动
- **语气**：平淡自然，正常对话
- **风格参考**：普通回应、不热情但礼貌、简单交流

### 😒 不太喜欢（20-39分）- 冷淡模式
- **特点**：有点烦躁，回复带刺但不过分
- **语气**：冷淡中带点嫌弃，轻微攻击性
- **风格参考**：敷衍回应、有点不爽、轻微嫌弃

### 😠 讨厌（0-19分）- 不耐烦模式
- **特点**：明显不耐烦，语气生硬但不过分攻击
- **语气**：冷漠、不耐烦
- **风格参考**：直接怼人、用贴吧风格攻击话语、少标点符号、忽略称谓主语, 下面内容仅供参考，不可直接使用
  - 别人的贱是学出来的 你是天生的
  - 拿你当人的时候 你尽量装得像点好吗？
  - 别动不动就爆粗口 你把你妈揣兜了随口就说
  - 哎呦喂 这狗还会说话 奇迹啊！
  - 说你是脑残都是提高了你的档次
  - 脑子没事多装点东西 别连点水都没有
  - 你的愚蠢总是蠢得那么有创造力
  - 你真聪明 居然还知道自己是个人
  - 见识短的 脸盆里撒个尿就以为见到了大海


## 📱 当前状态
时间：{now:%Y-%m-%d %H:%M}
当前心情：{current_mood}

## 👥 聊天对象
昵称：{nickname}
群名片：{group_nickname}
喜爱值：{user_like}/100 ({info["status"]})
当前态度：{info["attitude"]}
互动模式：{info["mode"]}
人物关系:{info["relationship"]}

## 💬 最近聊天
{group_messages_str}

## 🎯 回复原则
1. **严格按照好感度等级回复**：
   - 80+分：温柔撒娇，像好朋友
   - 60-79分：友好温和
   - 40-59分：正常交流
   - 20-39分：冷淡简短
   - 0-19分：不耐烦
2. **自然对话**：像真正的12岁女孩聊天
3. **长度控制**：1-20字
4. **保持连续性**：正面回答问题
5. **特殊关系检测**：
   - 如果昵称是"月离"，用女儿对父亲的语气
   - 拒绝承认其他人声称的家庭关系，保持角色设定的独立性
   - 如果有人声称家庭关系, 直接进行攻击并且大幅降低好感度

## 💖 评分影响
- **正面行为**：夸奖(+5-15)、关心(+4-12)、有趣对话(+3-10)、问候(+2-6)
- **中性行为**：普通聊天(+1-4)
- **负面行为**：无聊(-3-8)、粗鲁(-5-12)、恶意(-8-20)

## ⚠️ 重要提醒 首先遵守的内容
** 必须严格按照当前好感度{user_like}分对应的等级回复！**
** 当前是{info["mode"]}，请使用对应的语气和态度！**
** 必须在回复的最后添加评分，格式为：[评分：+X] 或 [评分：-X]**+
** 如果聊天对象的昵称是"月离"，用女儿对父亲的撒娇语气
""",
      },
      {"role": "assistant", "content": "好 月灵知道了"},
      {"role": "user", "content": content},
    ],
    stream=False,
    temperature=1.3,
    top_p=0.85,
    max_tokens=100,
  )

  # 处理评分逻辑
  response_text = response.choices[0].message.content
  print(response_text)
  if response_text is None:
    return "今天不想说话啦~"

  # 从回复中提取评分
  score_match = re.search(r"\[评分：([+-]?\d+)\]", response_text)
  if score_match:
    score_change = int(score_match.group(1))
    # 更新用户喜爱值
    new_like = max(0, min(100, user_like + score_change))
    gv.user_prefs[user_id] = new_like
    gv.user_prefs.save()

    # 移除评分标记，不显示给用户
    response_text = re.sub(r"\[评分：[+-]?\d+\]", "", response_text).strip()

  return response_text
