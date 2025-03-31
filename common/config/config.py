import ast
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv, set_key
from pydantic import BaseModel

load_dotenv()


YUELING_DATA_FOLDER = Path(os.getenv("YUELING_DATA_FOLDER") or "data")


def env_to_list(key):
  # 获取环境变量的值
  value = os.getenv(key)
  if value:
    try:
      # 使用 ast.literal_eval 安全地解析字符串为列表
      return ast.literal_eval(value)
    except (ValueError, SyntaxError):
      raise ValueError(f"Invalid format for environment variable {key}: {value}")
  return []


# 各种api的keys
class ApiConfig(BaseModel):
  deepl_auth_keys: list[str] = env_to_list("DEEPL_KEYS")
  deepseek_keys: list[str] = env_to_list("DEEPSEEK_KEYS")
  youtube_api_keys: list[str] = env_to_list("YOUTUBE_API_KEYS")


# Cookie配置
class CookieConfig(BaseModel):
  zhihu_cookies: str = os.getenv("ZHIHU_COOKIE") or ""
  weibo_cookies: str = os.getenv("WEIBO_COOKIE") or ""
  bilibili_cookies: str = os.getenv("BILIBILI_COOKIE") or ""

  def set_cookies(self, name: str, cookies: str):
    if name == "zhihu":
      self.zhihu_cookies = cookies
      set_key(dotenv_path=".env", key_to_set="ZHIHU_COOKIE", value_to_set=cookies)
    elif name == "weibo":
      self.weibo_cookies = cookies
      set_key(dotenv_path=".env", key_to_set="WEIBO_COOKIE", value_to_set=cookies)
    elif name == "bilibili":
      self.bilibili_cookies = cookies
      set_key(dotenv_path=".env", key_to_set="BILIBILI_COOKIE", value_to_set=cookies)
    else:
      ...


# 数据资源文件路径
class Resource(BaseModel):
  database: Path = Path()
  tmp: Path = Path()
  images: Path = Path()
  recycle: Path = Path()
  fonts: Path = Path()
  fortune: Path = Path()
  groups: Path = Path()


# 数据
class Data(BaseModel):
  database: Path = Path()
  group_black_list: Path = Path()
  group_ban_keywords: Path = Path()
  scheduler_config: Path = Path()
  group_members: Path = Path()


class User(BaseModel):
  tags: dict[str, list[str]] = {}


# 总配置
class Config(BaseModel):
  resource: Resource = Resource()
  data: Data = Data()
  user: User = User()
  api_cfg: ApiConfig = ApiConfig()
  cookie: CookieConfig = CookieConfig()
  id: str = str(uuid.uuid4())  # 启动程序唯一id 暂时没用


resource_paths = {
  "database": "database",
  "tmp": "tmp",
  "images": "images",
  "recycle": "recycle",
  "fonts": "fonts",
  "fortune": "fortune",
  "groups": "groups",
}

data_paths = {
  "database": "data.db",
  "group_black_list": "group_black_list.json",
  "group_ban_keywords": "group_ban_keywords.json",
  "group_members": "group_members.json",
  "scheduler_config": "scheduler_config.json",
}


config = Config(
  resource=Resource(**{key: YUELING_DATA_FOLDER / path for key, path in resource_paths.items()}),
  data=Data(**{key: YUELING_DATA_FOLDER / "database" / path for key, path in data_paths.items()}),
)
