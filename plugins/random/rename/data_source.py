import random

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

from common.base.Permission import Bot_admin_validate
from common.config.message import BotIsNotAdmin


async def group_change_name(bot: Bot, event: GroupMessageEvent, arg: str = ""):
  is_admin = await Bot_admin_validate(bot, event)
  if not is_admin:
    return BotIsNotAdmin

  el1 = [
    "废墟",
    "深海",
    "反应堆",
    "学园",
    "腐烂",
    "东京",
    "三维",
    "四次元",
    "流星",
    "闪光",
    "南极",
    "消极",
    "幽浮",
    "网路",
    "暗狱",
    "离子态",
    "液态",
    "黑色",
    "抱抱",
    "暴力",
    "垃圾",
    "残酷",
    "工口",
    "原味",
    "毛茸茸",
    "香香",
    "霹雳",
    "午夜",
    "美工刀",
    "爆浆",
    "机关枪",
    "无响应",
    "手术台",
    "麻风病",
    "虚拟",
    "速冻",
    "智能",
    "2000",
    "甜味",
    "华丽",
    "玛利亚",
    "无",
    "梦之",
    "蔷薇",
    "酷酷",
    "西伯利亚",
    "人造",
    "法外",
    "追杀",
    "通缉",
    "女子",
    "微型",
    "男子",
    "超",
    "毁灭",
    "大型",
    "绝望",
    "阴间",
    "死亡",
    "坟场",
    "高科技",
    "奇妙",
    "魔法",
    "极限",
    "无聊",
  ]
  el2 = [
    "小丑",
    "仿生",
    "纳米",
    "原子",
    "丧",
    "电子",
    "十字架",
    "咩咩",
    "赛博",
    "野猪",
    "外星",
    "窒息",
    "变态",
    "触手",
    "小众",
    "悲情",
    "飞行",
    "绿色",
    "电动",
    "铁锈",
    "碎尸",
    "电音",
    "蠕动",
    "酸甜",
    "虚构",
    "乱码",
    "碳水",
    "内脏",
    "脑浆",
    "血管",
    "绷带",
    "不合格",
    "光滑",
    "标本",
    "酸性",
    "碱性",
    "404",
    "变身",
    "反常",
    "樱桃",
    "碳基",
    "矫情",
    "病娇",
    "进化",
    "潮湿",
    "砂糖",
    "高潮",
    "变异",
    "复合盐",
    "伏特加",
    "抑郁",
    "暴躁",
    "不爱说话",
    "废物",
    "失败",
    "幻想型",
    "社恐",
    "苦涩",
    "粘液",
    "浓厚",
    "快乐",
    "强制",
    "中二病",
    "恶魔",
    "emo",
    "激光",
    "发射",
    "限量版",
    "迷因",
    "堕落",
    "放射性",
  ]
  el3 = [
    "天使",
    "精灵",
    "女孩",
    "男孩",
    "宝贝",
    "小妈咪",
    "虫",
    "菇",
    "公主",
    "少女",
    "少年",
    "1号机",
    "子",
    "恐龙",
    "蜈蚣",
    "蟑螂",
    "食人鱼",
    "小飞船",
    "舞女",
    "桃子",
    "团子",
    "精",
    "酱",
    "废料",
    "生物",
    "物质",
    "奶茶",
    "搅拌机",
    "液",
    "火锅",
    "祭司",
    "体",
    "实验品",
    "试验体",
    "小猫咪",
    "样本",
    "颗粒",
    "血块",
    "汽水",
    "蛙",
    "软体",
    "机器人",
    "人质",
    "小熊",
    "圣母",
    "胶囊",
    "乙女",
    "主义者",
    "屑",
    "垢",
    "污渍",
    "废人",
    "毛血旺",
    "怪人",
    "肉",
    "河豚",
    "豚",
    "藻类",
    "唾沫",
    "咒语",
    "建筑",
    "球",
    "小狗",
    "碳",
    "元素",
    "博士",
    "糖",
    "蜜罐",
    "蜡烛",
    "烟花",
    "雪花",
    "彩虹",
  ]

  name = random.choice(el1) + random.choice(el2) + random.choice(el3)

  if arg:
    name = arg

  await bot.set_group_card(group_id=event.group_id, user_id=event.user_id, card=name)
