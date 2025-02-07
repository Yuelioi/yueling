from functools import partial

from nonebot_plugin_alconna import on_alconna

from common.Alc.Alc import fullmatch, pm, ptc, register_handler
from plugins.random.daily.utils import get_drink, get_eat, get_fruit, get_game

pmg = partial(pm, group="随机")

__plugin_meta__ = pmg(
  name="吃喝玩乐图片",
  description="随机获取一款饮料",
  usage="""吃什么/喝什么/玩什么/来点水果""",
)


meta = ptc(__plugin_meta__)

_drink = fullmatch("随机喝的")
_drink.meta = ptc(__plugin_meta__)
drink = on_alconna(_drink, aliases={"喝啥", "喝什么", "来点喝的"})

_eat = fullmatch("随机吃的")
eat = on_alconna(_eat, aliases={"吃啥", "吃什么", "来点吃的"})

_play = fullmatch("随机玩的")
play = on_alconna(_play, aliases={"玩啥", "玩什么", "来点玩的"})

_fruit = fullmatch("随机水果")
fruit = on_alconna(_fruit, aliases={"来点水果"})


register_handler(drink, get_drink)
register_handler(eat, get_eat)
register_handler(play, get_game)
register_handler(fruit, get_fruit)
