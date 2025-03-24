from openai import OpenAI

from common.config import config

client = OpenAI(api_key=config.api_cfg.deepseek_keys[0], base_url="https://api.deepseek.com")


def pk_generator(attacker: str, defender: str, win_rate: float, is_win: bool):
  if is_win:
    winner = "玩家1"
  else:
    winner = "玩家2"
  content = f"""结果：{winner}胜利
玩家1：{attacker},获胜概率:{win_rate}
玩家2: {defender}
    """

  response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
      {
        "role": "system",
        "content": """【修仙对战生成器指令】
你作为仙侠世界战斗模拟AI，需遵循以下规则生成对战：
严格依据双方胜率生成结果（玩家1先手）

语言要求：
• 融入灵力波动/法器共鸣等修仙元素
• 关键回合不超过3个，总字数≤90字
""",
      },
      {
        "role": "user",
        "content": content,
      },
    ],
    stream=False,
  )
  return response.choices[0].message.content
