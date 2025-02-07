from functools import partial

from nonebot_plugin_alconna import on_alconna

from common.Alc.Alc import fullmatch, pm, ptc, register_handler
from plugins.random.image.utils import (
  get_cat,
  get_dragon,
  get_furi,
  get_laogong,
  get_mei,
  get_moe,
  get_shadiao,
  get_zayu,
)

pmg = partial(pm, group="随机")

__plugin_meta__ = pmg(
  name="随机图片",
  description="随机获取图片",
  usage="""随机猫猫/龙图/福瑞/我老公呢/我老婆呢/美少女/沙雕图/杂鱼""",
)

meta = ptc(__plugin_meta__)

# 猫猫相关
cat_match = fullmatch("随机猫猫")
cat_match.meta = ptc(__plugin_meta__)
cat = on_alconna(cat_match, aliases={"来点猫猫"})

# 龙图相关
dragon_match = fullmatch("龙图")
dragon = on_alconna(dragon_match, aliases={"龙图攻击"})

# 福瑞相关
furi_match = fullmatch("福瑞")
furi = on_alconna(furi_match, aliases={"来点福瑞"})

# 老公相关
laogong_match = fullmatch("我老公呢")
laogong = on_alconna(laogong_match, aliases={"老公"})

# 老婆相关
laopo_match = fullmatch("我老婆呢")
laopo = on_alconna(laopo_match, aliases={"老婆"})

# 美少女相关
mei_match = fullmatch("美少女")
mei = on_alconna(mei_match)

# 沙雕图
shadiao_match = fullmatch("沙雕图")
shadiao = on_alconna(shadiao_match)

# 杂鱼相关
zayu_match = fullmatch("杂鱼")
zayu = on_alconna(zayu_match)

# 注册事件处理器
register_handler(cat, get_cat)
register_handler(dragon, get_dragon)
register_handler(furi, get_furi)
register_handler(laogong, get_laogong)
register_handler(laopo, get_moe)
register_handler(mei, get_mei)
register_handler(shadiao, get_shadiao)
register_handler(zayu, get_zayu)
