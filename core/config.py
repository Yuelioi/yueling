"""应用配置加载 — 从 config.toml + .env 读取"""

import json
import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

_CONFIG_PATH = Path(os.getenv("YUELING_CONFIG_PATH") or "config.toml")
_DATA_DIR = Path(os.getenv("YUELING_DATA_FOLDER") or "data")


def _load_toml() -> dict:
  if _CONFIG_PATH.exists():
    with open(_CONFIG_PATH, "rb") as f:
      return tomllib.load(f)
  return {}


_toml = _load_toml()


def _env_list(key: str) -> list[str]:
  if value := os.getenv(key):
    try:
      parsed = json.loads(value)
      if isinstance(parsed, list):
        return [str(item) for item in parsed]
      return [str(parsed)]
    except (json.JSONDecodeError, ValueError):
      return [v.strip() for v in value.split(",") if v.strip()]
  return []


# ─── Config Models ───────────────────────────────────────────


class BotConfig(BaseModel):
  name: str = "月灵"
  owner_id: int = 0


class ProxyConfig(BaseModel):
  url: str = ""


class DatabaseConfig(BaseModel):
  path: str = "data/yueling.db"


class ApiConfig(BaseModel):
  deepl_auth_keys: list[str] = []
  deepseek_keys: list[str] = []
  youtube_api_keys: list[str] = []
  openai_keys: list[str] = []
  deepseek_base_url: str = "https://api.deepseek.com"
  cdn_base_url: str = "https://cdn.yuelili.com/bot"


class CookieConfig(BaseModel):
  zhihu: str = ""
  weibo: str = ""
  bilibili: str = ""


class PermissionsConfig(BaseModel):
  image_admins: list[int] = []


class PathsConfig(BaseModel):
  data: Path = _DATA_DIR
  database: Path = _DATA_DIR / "database"
  images: Path = _DATA_DIR / "images"
  tmp: Path = _DATA_DIR / "tmp"
  fonts: Path = _DATA_DIR / "fonts"
  fortune: Path = _DATA_DIR / "fortune"
  groups: Path = _DATA_DIR / "groups"
  recycle: Path = _DATA_DIR / "recycle"


class ProceduralConfig(BaseModel):
  max_rules_per_group: int = 10


class ProactiveConfig(BaseModel):
  enabled: bool = False
  min_confidence: float = 0.85
  cooldown_per_group: int = 600
  max_daily_per_group: int = 5
  trigger_keywords: list[str] = ["月灵"]
  context_window: int = 10


class AiConfig(BaseModel):
  procedural: ProceduralConfig = ProceduralConfig()
  proactive: ProactiveConfig = ProactiveConfig()


class AppConfig(BaseModel):
  bot: BotConfig = BotConfig()
  proxy: ProxyConfig = ProxyConfig()
  db: DatabaseConfig = DatabaseConfig()
  api: ApiConfig = ApiConfig()
  cookies: CookieConfig = CookieConfig()
  permissions: PermissionsConfig = PermissionsConfig()
  paths: PathsConfig = PathsConfig()
  ai: AiConfig = AiConfig()


# ─── Load ────────────────────────────────────────────────────


def _build_config() -> AppConfig:
  bot = _toml.get("bot", {})
  proxy = _toml.get("proxy", {})
  db = _toml.get("database", {})
  api_section = _toml.get("api", {})
  perms = _toml.get("permissions", {})
  ai_section = _toml.get("ai", {})

  ai_cfg = AiConfig(
    procedural=ProceduralConfig(**ai_section.get("procedural", {})),
    proactive=ProactiveConfig(**ai_section.get("proactive", {})),
  )

  return AppConfig(
    bot=BotConfig(**bot),
    proxy=ProxyConfig(**proxy),
    db=DatabaseConfig(**db),
    api=ApiConfig(
      deepl_auth_keys=_env_list("DEEPL_KEYS"),
      deepseek_keys=_env_list("DEEPSEEK_KEYS"),
      youtube_api_keys=_env_list("YOUTUBE_KEYS"),
      openai_keys=_env_list("OPENAI_KEYS"),
      **api_section,
    ),
    cookies=CookieConfig(
      zhihu=os.getenv("ZHIHU_COOKIE") or "",
      weibo=os.getenv("WEIBO_COOKIE") or "",
      bilibili=os.getenv("BILIBILI_COOKIE") or "",
    ),
    permissions=PermissionsConfig(**perms),
    paths=PathsConfig(),
    ai=ai_cfg,
  )


config = _build_config()


# ─── Plugin Config Helper ────────────────────────────────────


def get_plugin_config(plugin_name: str) -> dict:
  """读取 config.toml 中 [plugins.xxx] section"""
  return _toml.get("plugins", {}).get(plugin_name, {})
