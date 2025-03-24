from nonebot import on_fullmatch
from nonebot.plugin import PluginMetadata

from common.base.Handle import register_handler
from plugins.random.daily.utils import get_drink, get_eat, get_fruit, get_game

__plugin_meta__ = PluginMetadata(
  name="吃喝玩乐图片",
  description="随机获取一款饮料",
  usage="""吃什么/喝什么/玩什么/来点水果""",
  extra={
    "group": "随机",
    "commands": [
      "随机喝的",
      "喝啥",
      "喝什么",
      "来点喝的",
      "随机吃的",
      "吃啥",
      "吃什么",
      "来点吃的",
      "随机玩的",
      "玩啥",
      "玩什么",
      "来点玩的",
      "随机水果",
      "来点水果",
    ],
  },
)


drink = on_fullmatch(("随机喝的", "喝啥", "喝什么", "来点喝的"))

eat = on_fullmatch(("随机吃的", "吃啥", "吃什么", "来点吃的"))

play = on_fullmatch(("随机玩的", "玩啥", "玩什么", "来点玩的"))

fruit = on_fullmatch(("随机水果", "来点水果"))


register_handler(drink, get_drink)
register_handler(eat, get_eat)
register_handler(play, get_game)
register_handler(fruit, get_fruit)
