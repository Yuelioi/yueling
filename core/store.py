"""JSON 文件持久化 KV 存储（延迟写入）"""

import asyncio
import json
from pathlib import Path

from core.config import config


class JsonStore:
  def __init__(self, path: Path, write_delay: float = 1.0):
    self._path = path
    self._path.parent.mkdir(parents=True, exist_ok=True)
    self._data: dict = self._load()
    self._dirty = False
    self._write_delay = write_delay
    self._flush_handle: asyncio.TimerHandle | None = None

  def _load(self) -> dict:
    try:
      with open(self._path, encoding="utf-8") as f:
        return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
      return {}

  def _save(self):
    with open(self._path, "w", encoding="utf-8") as f:
      json.dump(self._data, f, ensure_ascii=False, indent=2)

  def _mark_dirty(self):
    if not self._dirty:
      self._dirty = True
      try:
        loop = asyncio.get_running_loop()
        self._flush_handle = loop.call_later(self._write_delay, self._flush)
      except RuntimeError:
        self._flush()

  def _flush(self):
    if self._dirty:
      self._save()
      self._dirty = False
      self._flush_handle = None

  def get(self, key, default=None):
    return self._data.get(str(key), default)

  def set(self, key, value):
    self._data[str(key)] = value
    self._mark_dirty()

  def setdefault(self, key, default=None):
    key = str(key)
    if key not in self._data:
      self._data[key] = default
      self._mark_dirty()
    return self._data[key]

  def delete(self, key):
    if str(key) in self._data:
      self._data.pop(str(key))
      self._mark_dirty()

  def save(self):
    self._flush()

  def all(self) -> dict:
    return self._data

  def __getitem__(self, key):
    return self._data[str(key)]

  def __setitem__(self, key, value):
    self._data[str(key)] = value
    self._mark_dirty()

  def __contains__(self, key):
    return str(key) in self._data


# ─── Store Instances ─────────────────────────────────────────

group_blacklist = JsonStore(config.paths.database / "group_black_list.json")
group_keywords = JsonStore(config.paths.database / "group_ban_keywords.json")
group_members = JsonStore(config.paths.database / "group_members.json")
user_tags = JsonStore(config.paths.database / "user_tags.json")
user_prefs = JsonStore(config.paths.database / "user_prefs.json")
