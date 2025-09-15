import random
import re

from nonebot.adapters.onebot.v11 import GroupMessageEvent

from common.base.Depends import Arg, Args, Img
from common.config import config, gv
from common.database.ImageManager import idb
from common.utils import api
from common.utils.rnd import get_random_image
from plugins.random.image.ba import get_random_image_by_tag


def split_tags(text: str) -> list:
  # 处理空字符串和纯空格情况
  if not text.strip():
    return []

  # 分割并过滤空标签
  return [tag.strip() for tag in re.split(r"\s*,\s*", text) if tag.strip()]


async def get_tags(arg: str = Arg()):
  tagsItems = idb.tags(arg, 16)[1:]
  res = ""
  for ti in tagsItems:
    res += f"{ti[0]}:{ti[1]}\n"
  return res.strip()


async def search_tags(img_url: str = Img(required=True)):
  imgdata = await api.fetch_image_from_url_ssl(img_url)
  tags = idb.search_image_by_hash(imgdata.getvalue())
  if tags:
    return ",".join(tags)
  else:
    return "暂时没有标签喔"


async def get_ba(args=Args(0, 99)):
  img_folder = "ba"
  if random_file := get_random_image(img_folder):
    return random_file

  if img := await get_random_image_by_tag("".join(args)):
    return img

  roles = [
    "阿罗娜",
    "普拉纳",
    "琪咲",
    "空崎雏",
    "星野",
    "圣园美卡",
    "宇泽雷萨",
    "小春",
    "玛丽",
    "宫子",
    "青亚",
    "丹花伊吹",
    "嬉笑教授",
    "霞泽美优",
    "内海青羽",
    "修波咯基",
    "屑之羽",
    "睦月",
    "阿露",
    "白梓",
    "阿慈谷",
    "柚",
    "爱丽丝",
    "心奈",
    "杏山和纱",
    "白子",
    "小桃",
    "飞鸟马时",
    "芹香",
    "调月莉奥",
    "群众",
  ]

  return "没有对应tag/没有数据:" + "/".join(roles)


async def get_cat():
  url = "http://edgecats.net/"
  if res := await api.fetch_image_from_url(url):
    return res


async def get_furi():
  img_folder = "福瑞"
  if random_file := get_random_image(img_folder):
    return random_file


def get_dragon():
  dragon_folder = "龙图"
  if random_file := get_random_image(dragon_folder):
    return random_file


async def get_moe(event: GroupMessageEvent, tags=Args(0)):
  # https://api.lolicon.app/setu/v2?tag=萝莉|少女&tag=白丝|黑丝
  # http://121.40.95.21/api/dm.php
  # https://www.dmoe.cc/random.php
  # https://api.ixiaowai.cn/api/api.php
  # https://api.yujn.cn/

  query_tags = split_tags(" ".join(tags)) or gv.user_tags.get(str(event.user_id), [])
  img_folder = "老婆"

  if event.user_id == 435826135 and not tags:
    img_folder = "pln"

  if query_tags:
    imgs = idb.search_images_by_tag(img_folder, query_tags)
    if imgs:
      img = random.choice(imgs)
      return config.resource.images / img_folder / img.filename
    # return "找不到符合您XP的图(请减少标签数量/检查标签是否正确)"
  if random_file := get_random_image(img_folder):
    return random_file


def get_laogong():
  img_folder = "老公"
  random_file = get_random_image(img_folder)
  if random_file := get_random_image(img_folder):
    return random_file


def get_shadiao():
  folder = "沙雕"
  random_file = get_random_image(folder)
  if random_file:
    return random_file


def get_zayu():
  random_file = get_random_image("杂鱼")
  if random_file:
    return random_file


def get_mei():
  img_folder = "美少女"
  random_file = get_random_image(img_folder)
  if random_file:
    return random_file
