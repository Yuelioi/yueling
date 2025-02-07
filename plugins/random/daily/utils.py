import random
from pathlib import Path

from common.config import config
from common.utils.draw import draw_grid


def get_images(folder_name: str):
  folder = config.resource.images / folder_name

  if not folder.exists():
    return "图片文件夹不存在"

  files: list[Path] = [file for file in folder.iterdir() if file.is_file()]

  if len(files) < 4:
    return "图片数量不足"
  random.shuffle(files)

  return draw_grid(files[:4])


def get_drink():
  print(get_images("喝的"))
  return get_images("喝的")


def get_eat():
  return get_images("吃的")


def get_fruit():
  return get_images("水果")


def get_game():
  return get_images("玩的")
