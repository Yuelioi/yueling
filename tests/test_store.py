"""测试 JsonStore 核心操作"""

import json
import tempfile
from pathlib import Path

from core.store import JsonStore


def test_store_basic_crud(tmp_path):
  store = JsonStore(tmp_path / "test.json", write_delay=0)

  store.set("key1", "value1")
  assert store.get("key1") == "value1"
  assert store.get("missing") is None
  assert store.get("missing", "default") == "default"

  store.set("key1", "updated")
  assert store.get("key1") == "updated"

  store.delete("key1")
  assert store.get("key1") is None


def test_store_persistence(tmp_path):
  path = tmp_path / "persist.json"
  store1 = JsonStore(path, write_delay=0)
  store1.set("hello", "world")
  store1.save()

  store2 = JsonStore(path, write_delay=0)
  assert store2.get("hello") == "world"


def test_store_setdefault(tmp_path):
  store = JsonStore(tmp_path / "sd.json", write_delay=0)
  result = store.setdefault("new_key", [1, 2, 3])
  assert result == [1, 2, 3]

  result = store.setdefault("new_key", [4, 5, 6])
  assert result == [1, 2, 3]


def test_store_contains(tmp_path):
  store = JsonStore(tmp_path / "c.json", write_delay=0)
  store.set("exists", True)
  assert "exists" in store
  assert "missing" not in store


def test_store_integer_keys(tmp_path):
  store = JsonStore(tmp_path / "int.json", write_delay=0)
  store.set(12345, {"score": 50})
  assert store.get(12345) == {"score": 50}
  assert store.get("12345") == {"score": 50}


def test_store_handles_corrupt_file(tmp_path):
  path = tmp_path / "bad.json"
  path.write_text("not valid json {{{", encoding="utf-8")
  store = JsonStore(path, write_delay=0)
  assert store.all() == {}
