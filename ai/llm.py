"""Unified LLM client — single AsyncOpenAI instance for the whole AI subsystem."""

from openai import AsyncOpenAI

from core.config import config

_client: AsyncOpenAI | None = None


def get_llm_client() -> AsyncOpenAI:
  global _client
  if _client is None:
    if not config.api.deepseek_keys:
      raise RuntimeError("DEEPSEEK_KEYS not configured")
    _client = AsyncOpenAI(
      api_key=config.api.deepseek_keys[0],
      base_url=config.api.deepseek_base_url,
    )
  return _client
