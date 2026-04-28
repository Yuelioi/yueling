"""业务逻辑层。不依赖 nonebot / ai / plugins。"""

import datetime
import random
import string

from services import external_api as api  # backward compat alias
from services.http_fetch import fetch_json, fetch_text, fetch_image  # noqa: F401
from services.qq_api import download_avatar  # noqa: F401
from services.fun_api import *  # noqa: F403
from services.html_parser import get_html, get_title, get_summary, get_keywords, fetch_page_data  # noqa: F401
from services.text_render import text_to_image
from services.downloader import download_img_proxy
from services.draw import draw_grid, random_item
from services.random_image import get_random_image, get_random_images
from services.translate import tran_deepl_pro, async_translate


def generate_random_code() -> str:
  characters = string.digits + string.ascii_letters
  return "".join(random.choice(characters) for _ in range(6))


def generate_timestamp() -> str:
  return datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")[:-4]


__all__ = [
  "api",
  "fetch_json", "fetch_text", "fetch_image",
  "download_avatar",
  "text_to_image", "download_img_proxy",
  "draw_grid", "random_item",
  "get_random_image", "get_random_images",
  "tran_deepl_pro", "async_translate",
  "generate_random_code", "generate_timestamp",
  "get_html", "get_title", "get_summary", "get_keywords", "fetch_page_data",
]
