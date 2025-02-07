import os
import random
from pathlib import Path

from common.config import config


def get_random_image(folder_name: str, keyword: str | None = None):
  """Get random image from target folder\n
  If dont exist keyword, target =  all files.
  """
  all_files = get_random_images(folder_name, keyword)
  if all_files:
    return Path(random.choice(all_files))


def get_random_images(folder_name: str, keyword: str | None = None, num_images=0):
  """Get random images from target folder\n
  If dont exist keyword return all files.
  """
  folder = config.resource.images / folder_name
  all_files: list[Path] = []

  for root, dirs, files in os.walk(folder):
    for file in files:
      file_path = os.path.join(root, file)
      if keyword and keyword not in file:
        continue
      all_files.append(Path(file_path))

  # 随机选择 num_images 个文件, 如果没有设置数量, 则返回所有

  if num_images:
    return random.sample(all_files, min(num_images, len(all_files)))

  return all_files
