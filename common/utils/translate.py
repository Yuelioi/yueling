import random

import deepl

from common.config import config


def tran_deepl_pro(text: str, source_lang=None, target_lang="zh"):
  if not config.api_cfg.deepl_auth_keys:
    return "翻译服务未配置,请联系管理员"
  key = random.choice(config.api_cfg.deepl_auth_keys)

  translator = deepl.translator.Translator(key)
  result = translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)

  return result.text if isinstance(result, deepl.TextResult) else "翻译报错,请联系管理员"  # type: ignore
