import concurrent.futures
import hashlib
import os
import random
from datetime import datetime
from io import BytesIO
from pathlib import Path

from nonebot import logger
from sqlalchemy import Column, DateTime, Integer, String

from common.config import config
from common.database.DBBase import DBManagerBase
from common.models import ImageData


def calculate_md5(target: Path | bytes):
  md5 = hashlib.md5()

  if isinstance(target, Path):
    with open(target, "rb") as file:
      for chunk in iter(lambda: file.read(4096), b""):
        md5.update(chunk)
  else:
    md5.update(target)
  return md5.hexdigest()


def get_modified_time(file_path: Path):
  modification_time_timestamp = os.path.getmtime(file_path)
  modification_time = datetime.fromtimestamp(modification_time_timestamp)
  return modification_time


def process_image(cat, img_path):
  return ImageData(
    path=str(img_path),
    category=cat,
    uploader=0,
    upload_time=get_modified_time(img_path),
    hash=calculate_md5(img_path),
  )


class ImageManager(DBManagerBase):
  def _create_table_fields(self):
    self.table_fields = [
      Column("id", Integer, primary_key=True),
      Column("path", Integer, unique=True),
      Column("category", String(128), nullable=True),
      Column("uploader", String(128), nullable=True),
      Column("upload_time", DateTime, nullable=True),
      Column("hash", String(128), nullable=True),
      Column("score", String(128), nullable=True),
    ]

  # 重构索引
  def reset_data(self):
    self._clear_data()
    cats = [
      "表情包",
      "吃的",
      "存档",
      "福瑞",
      "喝的",
      "老公",
      "老婆",
      "零食",
      "龙图",
      "美少女",
      "拍一拍",
      "沙雕",
      "水果",
      "玩的",
      "语录",
      "杂鱼",
    ]
    imgdatas = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
      futures = []
      for cat in cats:
        folder = Path(config.resource.images) / cat
        for img_path in folder.glob("**/*.*"):
          futures.append(executor.submit(process_image, cat, img_path))

      for future in concurrent.futures.as_completed(futures):
        imgdatas.append(future.result())

    self.insert_datas(imgdatas)

  def query_images(self, cat: str, num: int = 9):
    """根据分类 获取指定个数随机图片信息"""
    all_data = self.conn.execute(self.table.select().where(self.table.c.category == cat)).fetchall()
    random_items = random.sample(all_data, min(num, len(all_data)))

    return self.to_dicts(random_items)

  def check_hash(self, data: bytes):
    """检查是否存在该md5"""
    if self.conn.execute(self.table.select().where(self.table.c.hash == data)).fetchone():
      return True
    return False

  # 如果没有找到, 返回新文件md5, 找到就返回 False
  def check_duplicate_images(self, data: bytes):
    """检查数据库是否有相同md5值"""
    md5 = calculate_md5(data)

    if not self.conn.execute(self.table.select().where(self.table.c.hash == md5)).fetchone():
      return md5

  def search_image(self, hash: str):
    """获取图片信息"""

    # 如果找到 则返回文件数据
    if result := self.conn.execute(self.table.select().where(self.table.c.hash == hash)).fetchone():
      return self.to_dict(result)
    else:
      return False

  def remove_image(self, source: BytesIO):
    """删除图片数据"""

    data = source.getvalue()
    hash = calculate_md5(data)
    result = im.search_image(hash)

    if result:
      try:
        self.conn.execute(self.table.delete().where(self.table.c.hash == hash))
        self.conn.commit()
        return result, None
      except Exception as e:
        logger.error(e)
        return None, e
    else:
      return None, "未找到数据"

  def image_summary(self):
    result = self.conn.execute(self.table.select().with_only_columns(self.table.c.category))
    data = []
    from collections import Counter

    for row in result:
      data.append(row[0])

    counter = Counter(data)

    sorted_counts = sorted(counter.items(), key=lambda x: x[1])

    msg = ""
    # 打印结果
    for element, count in sorted_counts:
      if element == "存档":
        continue
      if count < 10:
        continue
      msg += f"{element}: 共{count}个\n"

    return msg.strip()


im = ImageManager(db_path=config.data.database, table_name="image")
