import json
from dataclasses import dataclass
from typing import ClassVar, Optional

from common.config import config


def load_or_create_json(file_path):
  try:
    with open(file_path, encoding="utf-8") as f:
      return json.load(f)
  except FileNotFoundError:
    default_data = {}
    with open(file_path, "w", encoding="utf-8") as f:
      json.dump(default_data, f, ensure_ascii=False, indent=4)
    return default_data


@dataclass
class GV:
  _instance: Optional["GV"] = None
  _group_black_list: ClassVar[dict] = load_or_create_json(config.data.group_black_list)
  _group_ban_keywords: ClassVar[dict] = load_or_create_json(config.data.group_ban_keywords)

  def __post_init__(self):
    self.group_black_list = self.__class__._group_black_list
    self.group_ban_keywords = self.__class__._group_ban_keywords

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance


gv = GV()
