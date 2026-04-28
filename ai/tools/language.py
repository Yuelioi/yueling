"""AI 内置工具 — 语言处理（翻译、解释）"""

from ai.registry import ai_tool
from core.context import ToolContext
from services.translate import translate as svc_translate


@ai_tool(
  description="翻译文本到目标语言（默认中文）",
  triggers=["翻译", "translate"],
  patterns=[r"把.+翻译成", r"译成.+"],
  semantic_slots=["翻译", "语言转换", "中英互译", "译成"],
  tags=["language"],
  examples=["翻译 hello", "把这段译成英文", "翻译成日语：今天天气真好"],
)
async def translate_text(ctx: ToolContext, text: str, target: str = "zh") -> str:
  """翻译文本

  Args:
    text: 要翻译的内容
    target: 目标语言代码（zh/en/ja/ko/fr/de/es/ru），默认 zh
  """
  return await svc_translate(text, target=target)
