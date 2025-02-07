from common.utils import api
from common.utils.rnd import get_random_image


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


def get_moe():
  # https://api.lolicon.app/setu/v2?tag=萝莉|少女&tag=白丝|黑丝
  # http://121.40.95.21/api/dm.php
  # https://www.dmoe.cc/random.php
  # https://api.ixiaowai.cn/api/api.php
  # https://api.yujn.cn/

  img_folder = "老婆"
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
