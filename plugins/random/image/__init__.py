from nonebot import on_fullmatch
from nonebot.plugin import PluginMetadata

from common.base.Handle import register_handler
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

__plugin_meta__ = PluginMetadata(
  name="随机图片",
  description="随机获取图片",
  usage="""随机猫猫/龙图/福瑞/我老公呢/我老婆呢/美少女/沙雕图/杂鱼""",
  extra={"group": "随机", "commands": ["随机猫猫", "龙图", "福瑞", "我老公呢", "我老婆呢", "美少女", "沙雕图", "杂鱼"]},
)


cat = on_fullmatch(("随机猫猫", "来点猫猫"))


dragon = on_fullmatch(("龙图", "龙图攻击"))

furi = on_fullmatch(("福瑞", "来点福瑞"))

laogong = on_fullmatch(("我老公呢", "老公"))

laopo = on_fullmatch(("我老婆呢", "老婆"))

mei = on_fullmatch("美少女")

shadiao = on_fullmatch("沙雕图")

zayu = on_fullmatch("杂鱼")

# 注册事件处理器
register_handler(cat, get_cat)
register_handler(dragon, get_dragon)
register_handler(furi, get_furi)
register_handler(laogong, get_laogong)
register_handler(laopo, get_moe)
register_handler(mei, get_mei)
register_handler(shadiao, get_shadiao)
register_handler(zayu, get_zayu)
