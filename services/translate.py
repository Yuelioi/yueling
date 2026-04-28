"""翻译业务逻辑。

只接受基本类型；不知道 nonebot / ToolContext / Bot / Event。
service 层不依赖 nonebot / ai / plugins，仅依赖 core 与第三方库。
"""

from __future__ import annotations

import asyncio
import random

import deepl

from core.config import config


# ─── DeepL ────────────────────────────────────────────────────


def _pick_deepl_key() -> str | None:
  if not config.api.deepl_auth_keys:
    return None
  return random.choice(config.api.deepl_auth_keys)


# DeepL 目标语言代码归一化
_DEEPL_LANG = {
  "zh": "ZH-HANS",
  "zh-hans": "ZH-HANS",
  "zh-cn": "ZH-HANS",
  "en": "EN-US",
  "en-us": "EN-US",
  "en-gb": "EN-GB",
  "ja": "JA",
  "ko": "KO",
  "fr": "FR",
  "de": "DE",
  "es": "ES",
  "ru": "RU",
}

SUPPORTED_LANGS: frozenset[str] = frozenset(_DEEPL_LANG.keys())


def tran_deepl_pro(text: str, source_lang=None, target_lang="zh"):
  """旧版同步入口 — 保留以兼容 plugins/tools/link_analysis/* 与 services/__init__ 重导出。"""
  if not config.api.deepl_auth_keys:
    return "翻译服务未配置,请联系管理员"
  key = random.choice(config.api.deepl_auth_keys)

  translator = deepl.translator.Translator(key)
  result = translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)

  return result.text if isinstance(result, deepl.TextResult) else "翻译报错,请联系管理员"  # type: ignore


async def async_translate(text: str, source_lang=None, target_lang="zh") -> str:
  """旧版异步入口 — 同上，保留兼容。"""
  return await asyncio.to_thread(tran_deepl_pro, text, source_lang, target_lang)


# ─── 新版统一入口 ─────────────────────────────────────────────


async def translate(text: str, target: str = "zh") -> str:
  """翻译文本到目标语言。

  失败路径全部 return 字符串（错误信息也是字符串），不抛异常 —
  调用方拿到的总是 `str`，便于命令层直接发送。
  """
  if not text or not text.strip():
    return "请提供要翻译的文本"

  deepl_lang = _DEEPL_LANG.get(target.lower())
  key = _pick_deepl_key()
  if key and deepl_lang:
    try:
      result = await asyncio.to_thread(_deepl_translate_sync, key, text, deepl_lang)
      if result:
        return result
    except deepl.DeepLException:
      pass  # 降级到 LLM
    except Exception:
      pass  # 网络/超时等任何异常都降级，不抛

  return await _translate_via_llm(text, target)


def _deepl_translate_sync(key: str, text: str, target_lang: str) -> str:
  translator = deepl.translator.Translator(key)
  result = translator.translate_text(text, target_lang=target_lang)
  if isinstance(result, deepl.TextResult):
    return result.text
  return ""


async def _translate_via_llm(text: str, target: str) -> str:
  """LLM 兜底翻译 — 不依赖 ai.llm，自建 client 保持 service 层独立。"""
  from openai import AsyncOpenAI

  if not config.api.deepseek_keys:
    return "翻译失败：未配置翻译服务"

  client = AsyncOpenAI(
    api_key=config.api.deepseek_keys[0],
    base_url=config.api.deepseek_base_url or None,
  )
  try:
    resp = await client.chat.completions.create(
      model="deepseek-v4-flash",
      messages=[
        {
          "role": "system",
          "content": (
            f"You are a translator. Translate the user's text to {target}. "
            "Output only the translation, no explanations."
          ),
        },
        {"role": "user", "content": text},
      ],
      temperature=0.0,
      max_tokens=500,
    )
    content = resp.choices[0].message.content
    return content.strip() if content else "翻译失败"
  except Exception as e:
    return f"翻译失败: {e}"
