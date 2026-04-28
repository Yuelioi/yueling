"""Unified LLM client — single AsyncOpenAI instance for the whole AI subsystem."""

from openai import AsyncOpenAI

from core.config import config

_client: AsyncOpenAI | None = None

DEFAULT_MODEL = "deepseek-v4-flash"


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


async def llm_complete(
  system: str,
  user_content: str,
  temperature: float = 0.3,
  max_tokens: int = 200,
  fallback: str = "",
) -> str:
  resp = await get_llm_client().chat.completions.create(
    model=DEFAULT_MODEL,
    messages=[
      {"role": "system", "content": system},
      {"role": "user", "content": user_content},
    ],
    temperature=temperature,
    max_tokens=max_tokens,
  )
  return resp.choices[0].message.content or fallback
