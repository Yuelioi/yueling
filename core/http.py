import httpx
from nonebot import get_driver

from core.config import config

_client: httpx.AsyncClient | None = None

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"


def get_client() -> httpx.AsyncClient:
  if _client is None:
    raise RuntimeError("HTTP client not initialized. Call init_client() first.")
  return _client


def get_proxy_client() -> httpx.AsyncClient:
  """Returns a NEW client with proxy configured (caller must close or use as context manager)."""
  return httpx.AsyncClient(
    proxy=config.proxy.url or None,
    headers={"User-Agent": USER_AGENT},
    timeout=httpx.Timeout(30.0),
    follow_redirects=True,
  )


async def init_client():
  global _client
  _client = httpx.AsyncClient(
    headers={"User-Agent": USER_AGENT},
    timeout=httpx.Timeout(30.0),
    follow_redirects=True,
  )


async def close_client():
  global _client
  if _client:
    await _client.close()
    _client = None


def _register_hooks():
  driver = get_driver()

  @driver.on_startup
  async def _startup():
    await init_client()

  @driver.on_shutdown
  async def _shutdown():
    await close_client()


try:
  _register_hooks()
except Exception:
  pass
