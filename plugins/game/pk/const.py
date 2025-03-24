REGISTER_POWER = 100
REGISTER_MONEY = 1000

SIGN_POWER = 100
SIGN_MONEY = 500

# 时机
BEFORE_SIGN = "签到前"

GAME_END = "游戏前"
GAME_START = "游戏后"

BEFORE_ATTACK = "攻击前"
AFTER_ATTACK = "攻击后"

BEFORE_DEFEND = "防御前"
AFTER_DEFEND = "防御后"


# 属性
POWER = "战斗力"
MONEY = "金币"


# Buff
BUFFS = {
  "初入江湖": {"description": "增加签到奖励", "duration": 7, "effects": [{"money": 100, "power": 100, "apply_time": BEFORE_SIGN}]},
  # "新手保护": {"description": "对局不会受到惩罚", "duration": 7, "apply_time": GAME_END, "effects": {}},
}
# Status
