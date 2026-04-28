"""Backward-compat re-exports — prefer importing from the specific module directly."""

from services.http_fetch import fetch_json as fetch_json_from_url  # noqa: F401
from services.http_fetch import fetch_text as fetch_text_from_url  # noqa: F401
from services.http_fetch import fetch_image as fetch_image_from_url  # noqa: F401
from services.http_fetch import fetch_image as fetch_image_from_url_ssl  # noqa: F401
from services.qq_api import download_avatar  # noqa: F401
from services.fun_api import (  # noqa: F401
  shadiao,
  xiaoheizi,
  chat,
  chi,
  chaijun,
  fun_gif,
  tiangou,
  lvcha,
  shenhuifu,
  kfc,
  read60s,
  trace,
  read60s_2,
)
from services.html_parser import (  # noqa: F401
  get_html,
  get_title,
  get_summary,
  get_keywords,
  fetch_page_data as fetch_data,
)
