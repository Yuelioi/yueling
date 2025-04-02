from datetime import datetime
from typing import TypedDict

import aiohttp
from openai import OpenAI

from common.config import config, gv


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
  return "\n".join(f"[{msg['nickname']} ➔ {msg['text']}]" for msg in processed[-11:-1])


def chat_ai(content: str, user_info: GroupMemberInfo, raw_messages: list):
  # 用户基础信息
  user_id = str(user_info["user_id"])
  nickname = user_info["nickname"]
  group_nickname = user_info["card"]
  now = datetime.now()

  # 读取用户喜好数据
  user_preferences = gv.user_prefs.get(user_id, [])
  prefs_str = "、".join(user_preferences) if user_preferences else "暂无记录"

  # 获取聊天记录
  group_messages_str = convert_messages(raw_messages)

  response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
      {
        "role": "system",
        "content": f"""# 角色设定
你是叫月灵的8岁小女孩，拥有以下特征：
* 说话自然可爱
* 回复简短（100字以内）
* 父亲是月离（不可主动提及）


# 对话指南
## 当前时间
{now:%Y-%m-%d %H:%M}

## 用户档案
┏ ID：{user_id}
┣ 昵称：{nickname}
┣ 群名片：{group_nickname}
┗ 喜好：{prefs_str}

## 上下文参考
群聊天记录格式为：
昵称 ➔ 消息内容

示例：
小可爱 ➔ 今天午餐吃什么呢？
Tech君 ➔ 推荐试试食堂新菜

当前聊天记录：
{group_messages_str}

## 回复要求
1. 优先结合当前对话内容
2. 仅在用户主动提起或上下文相关时自然带出喜好
3. 不要直接复述记录中的昵称和消息
4. 用日常口语表达，例如：
   正确："好呀～要一起看新番吗？(≧ω≦)
   错误："根据您喜欢的动漫，建议一起观看新番"
""",
      },
      {"role": "assistant", "content": "好哒～月灵知道啦~"},
      {"role": "user", "content": content},
    ],
    stream=False,
  )

  return response.choices[0].message.content
