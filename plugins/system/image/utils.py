import datetime
import os

import aiofiles
from nonebot import logger

from common.config import config
from common.database.ImageManager import ImageData, im
from common.utils import api, generate_random_code, generate_timestamp


def detect_image_type(data):
  # 定义常见图片类型的魔数
  image_magic_numbers = {
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG\r\n\x1a\n": "png",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
  }

  # 检查字节流的开头几个字节来判断图片类型
  for magic_number, image_type in image_magic_numbers.items():
    if data.startswith(magic_number):
      return image_type

  # 如果无法确定类型，则返回 None
  return None


def name_gene(cmd: str = "", filename: str = "", group="", uploader=""):
  if cmd in [
    "添加老婆",
    "添加老公",
    "添加老公",
    "添加龙图",
    "添加杂鱼",
    "添加沙雕图",
    "添加美少女",
    "添加福瑞",
  ]:
    return generate_timestamp()

  if cmd in ["添加表情"]:
    return filename + "_" + generate_random_code()

  if cmd in ["添加吃的", "添加喝的", "添加水果", "添加玩的", "添加零食"]:
    return filename

  if cmd in ["添加拍一拍"]:
    return uploader

  if cmd in ["添加语录"]:
    return f"{group}_{filename}_{generate_random_code()}"

  else:
    # "添加存档": "存档",
    return generate_random_code()


async def add_images(cmd: str, group_id, user_id, arg: str, imgs: list[str] = []):
  msgs = ""

  for index, img in enumerate(imgs):
    virtual_file = await api.fetch_image_from_url_ssl(img)

    img_data = virtual_file.read()

    file_hash = im.check_duplicate_images(img_data)
    if not file_hash:
      return "图片重复啦"

    trg_name = name_gene(cmd, arg, group_id, user_id)
    cat = cmd.replace("添加", "").replace("沙雕图", "图").replace("表情包", "包")

    suffix = detect_image_type(img_data)

    trg_path = f"{config.resource.images}/{cat}/{trg_name}.{suffix}"
    logger.info(f"图片{index + 1}保存路径:{trg_path}")

    try:
      async with aiofiles.open(trg_path, "wb") as f:
        await f.write(img_data)

      ret = im.insert_data(
        ImageData(
          path=trg_path,
          category=cat,
          uploader=user_id,
          upload_time=datetime.datetime.now(),
          hash=file_hash,
          score=0,
        )
      )

      if ret:
        msgs += f"图片{index + 1}上传成功\n"
        logger.info(f"上传图片:{trg_path}")
    except Exception as e:
      logger.info(f"上传图片失败:{trg_path}", e)
      msgs += f"图片{index + 1}上传失败{e}\n"
  return msgs


async def delete_image(user_id: int, img: str):
  """删除图片 并加入回收站"""

  if user_id not in [435826135, 963036493, 1239245970, 1284773289, 405850498]:
    return "就凭你也想访问本小姐的系统!"

  if not img:
    return "图片链接错误"

  virtual_file = await api.fetch_image_from_url_ssl(img)
  result, err = im.remove_image(virtual_file)
  if err is None:
    if result:
      img_path = result["path"]
      os.rename(img_path, os.path.join(config.resource.recycle, os.path.basename(img_path)))
      return "删除成功"
    else:
      return "图片不存在"
  else:
    return "删除失败:" + str(err)


async def image_summary():
  """统计图片数据库: 清空数据库并重新读取"""
  return im.image_summary()


async def update_image_database():
  """更新图片数据库: 清空数据库并重新读取"""
  im.reset_data()
  return "更新完毕"
