import random

from nonebot import on_fullmatch
from nonebot.plugin import PluginMetadata

from core.config import config
from core.handler import register_handler
from core.context import ToolContext
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
    "tools": [{
      "name": "recommend_food",
      "description": "随机推荐吃的/喝的/玩的/水果",
      "tags": ["fun", "random"],
      "examples": ["吃什么好", "推荐点喝的", "今天玩什么", "来点水果"],
      "parameters": {
        "category": {"type": "string", "description": "分类: eat/drink/play/fruit", "default": "eat"},
      },
      "handler": "recommend_tool_handler",
    }],
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

CATEGORY_MAP = {"eat": "吃的", "drink": "喝的", "play": "玩的", "fruit": "水果"}


async def recommend_tool_handler(ctx: ToolContext, category: str = "eat") -> str:
  folder_name = CATEGORY_MAP.get(category, "吃的")
  folder = config.paths.images / folder_name
  if not folder.exists():
    return f"没有{folder_name}的推荐数据"
  files = [f.stem for f in folder.iterdir() if f.is_file()]
  if not files:
    return f"没有{folder_name}的推荐数据"
  picks = random.sample(files, min(4, len(files)))
  return f"推荐{folder_name}: " + "、".join(picks)
