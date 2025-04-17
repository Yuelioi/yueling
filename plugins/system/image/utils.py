from nonebot import logger

from common.database.ImageManager import calculate_hash, idb
from common.utils import api, generate_random_code


def detect_image_type(data: bytes):
  # 定义常见图片类型的魔数
  image_magic_numbers = {
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG\r\n\x1a\n": "png",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
  }

  for magic_number, image_type in image_magic_numbers.items():
    if data.startswith(magic_number):
      return image_type

  return "jpg"


def name_gene(cmd: str = "", filename: str = "", group="", uploader=""):
  # hash文件名
  if cmd in ["添加老婆", "添加老公", "添加龙图", "添加杂鱼", "添加沙雕图", "添加美少女", "添加福瑞", "添加ba"]:
    return ""

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


async def add_images(cmd: str, group_id: int, user_id: int, arg: str, imgs: list[str] = []):
  msgs = ""

  if cmd == "添加ba" and not user_id == 435826135:
    return "权限不足!!"

  for index, img in enumerate(imgs):
    virtual_file = await api.fetch_image_from_url_ssl(img)
    try:
      img_data = virtual_file.read()
      filename = name_gene(cmd, arg, str(group_id), str(user_id))
      cat = cmd.replace("添加", "").replace("表情包", "包")
      suffix = detect_image_type(img_data)
      idb.add_image(cat, img_data, suffix, filename)
      logger.info(f"上传图片:{cat}/{filename}")
      msgs += f"图片{index + 1}上传成功\n"

    except Exception as e:
      logger.info(f"上传图片失败:{e}")
      msgs += f"图片{index + 1}上传失败{e}\n"
  return msgs.strip()


async def delete_image(user_id: int, img: str):
  """删除图片 并加入回收站"""

  if user_id not in [435826135, 963036493, 1239245970, 1284773289, 405850498]:
    return "就凭你也想访问本小姐的系统!"

  if not img:
    return "图片链接错误"

  virtual_file = await api.fetch_image_from_url_ssl(img)
  img_data = virtual_file.read()
  filehash = calculate_hash(img_data)
  try:
    idb.delete_image(filehash)
    return "删除成功"
  except Exception as e:
    return f"删除失败{e}"


async def image_summary():
  """统计图片数据库: 清空数据库并重新读取"""
  return


async def update_image_database():
  """更新图片数据库: 清空数据库并重新读取"""

  return
