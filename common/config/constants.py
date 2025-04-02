import json
from collections import UserDict
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from common.config import config


class ConfigDict(UserDict):
  """支持自动保存的配置字典"""

  def __init__(self, file_path: Path, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._file_path = file_path

  def save(self):
    """保存数据到关联文件"""
    self._file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(self._file_path, "w", encoding="utf-8") as f:
      json.dump(self.data, f, ensure_ascii=False, indent=2)


def load_or_create_json(file_path: Path) -> ConfigDict:
  """加载或创建配置字典"""
  try:
    with open(file_path, encoding="utf-8") as f:
      data = json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
    data = {}

  config_dict = ConfigDict(file_path, data)
  if not file_path.exists():
    config_dict.save()
  return config_dict


@dataclass
class GV:
  _instance: Optional["GV"] = None

  _group_black_list: ClassVar[ConfigDict] = load_or_create_json(config.resource.database / "group_black_list.json")
  _group_ban_keywords: ClassVar[ConfigDict] = load_or_create_json(config.resource.database / "group_ban_keywords.json")
  _group_members: ClassVar[ConfigDict] = load_or_create_json(config.resource.database / "group_members.json")
  _user_tags: ClassVar[ConfigDict] = load_or_create_json(config.resource.database / "user_tags.json")
  _user_prefs: ClassVar[ConfigDict] = load_or_create_json(config.resource.database / "user_prefs.json")

  def __post_init__(self):
    self.group_black_list = self.__class__._group_black_list
    self.group_ban_keywords = self.__class__._group_ban_keywords
    self.group_members = self.__class__._group_members
    self.user_tags = self.__class__._user_tags
    self.user_prefs = self.__class__._user_prefs

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  def save(self, *config_names: str):
    """
    批量保存配置（兼容原有接口）
    :param config_names: 可接受多个配置名称，不传则保存全部
    """
    config_map = {
      "group_black_list": self.group_black_list,
      "group_ban_keywords": self.group_ban_keywords,
      "group_members": self.group_members,
      "user_tags": self.user_tags,
    }

    targets = config_names or config_map.keys()
    for name in targets:
      if name not in config_map:
        raise ValueError(f"未知配置项: {name}")
      config_map[name].save()


gv = GV()
