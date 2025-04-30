from collections import OrderedDict

# 最大存储容量
MAX_CAPACITY = 200
image_dict = OrderedDict()

import aiohttp
from tortoise.expressions import RawSQL

from common.models.ba import Image

roles = {
  "阿罗娜": "アロナ(ブルーアーカイブ)",
  "普拉娜": "プラナ(ブルーアーカイブ)",
  "琪咲": "キサキ(ブルーアーカイブ)",
  "空崎雏": "空崎ヒナ",
  "星野": "小鳥遊ホシノ",
  "圣园美卡": "聖園ミカ",
  "宇泽雷萨": "宇沢レイサ",
  "小春": "下江コハル",
  "玛丽": "伊落マリー",
  "宫子": "月雪ミヤコ",
  "青亚": "百合園セイア",
  "丹花伊吹": "丹花イブキ",
  "嬉笑教授": "ニヤニヤ教授",
  "霞泽美优": "霞沢ミユ",
  "内海青羽": "内海アオバ",
  "修波咯基": "シュポガキ",
  "屑之羽": "クズノハ(ブルーアーカイブ)",
  "睦月": "浅黄ムツキ",
  "阿露": "陸八魔アル",
  "白梓": "白洲アズサ",
  "阿慈谷": "阿慈谷ヒフミ",
  "夏": "柚鳥ナツ",
  "爱丽丝": "天童アリス",
  "心奈": "春原ココナ",
  "杏山和纱": "杏山カズサ",
  "白子": "砂狼シロコ",
  "小桃": "才羽モモイ",
  "飞鸟马时": "飛鳥馬トキ",
  "芹香": "黒見セリカ",
  "调月莉奥": "調月リオ",
  "群众": "正義実現委員会のモブ",
  "随机": "",
}


async def get_random_image_by_tag(tag: str):
  filters = {"score": 100}

  if tag:
    tag_jp = roles.get(tag)
    if isinstance(tag_jp, list):
      tag_jp = tag_jp[0]
    if tag_jp:
      filters["tags__contains"] = [tag_jp]  # type: ignore

  images = await Image.filter(**filters).annotate(random_order=RawSQL("random()")).order_by("random_order").limit(1)

  if images:
    img = images[0]
    image_bytes = await fetch_image(img.urls["regular"])
    image_hash = hash(image_bytes)

    if len(image_dict) >= MAX_CAPACITY:
      image_dict.popitem(last=False)

    image_dict[image_hash] = img.id

    return image_bytes

  return None


async def set_score(image_hash: str, score: int):
  img_id = image_dict.get(image_hash)
  if not img_id:
    return
  image = await Image.get(id=img_id)
  score = max(min(score, 100), -100)

  if image:
    image.score = score
    await image.save()

    return True
  return False


async def fetch_image(url: str):
  # 设置请求头，包括 Referer
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.pixiv.net/",
  }

  # 发起异步请求
  try:
    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
        if response.status != 200:
          raise Exception(f"Failed to fetch image, status: {response.status}")

        image_bytes = await response.read()
        return image_bytes
  except Exception as e:
    raise Exception(f"Error fetching image: {e}")
