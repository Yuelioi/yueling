"""AI 内置工具 — 知识能力（摘要、编程、汇率）"""

from ai.llm import llm_complete
from ai.registry import tool
from core.context import ToolContext
from core.http import get_client


@tool(
  tags=["language"],
  examples=["帮我总结这段话", "概括一下", "太长不看"],
)
async def summarize_text(ctx: ToolContext, text: str) -> str:
  """将长文本压缩为简短摘要，保留要点

  Args:
    text: 需要摘要的文本
  """
  if len(text) < 20:
    return "文本太短，不需要摘要"
  try:
    return await llm_complete(
      "用3-5个要点总结以下内容，每个要点一句话。简洁直接。",
      text[:3000],
      temperature=0.2,
      max_tokens=300,
      fallback="无法总结",
    )
  except Exception as e:
    return f"摘要失败: {e}"


@tool(
  tags=["math", "info"],
  examples=["100美元等于多少人民币", "日元换算", "汇率查询"],
)
async def convert_currency(ctx: ToolContext, amount: float, source: str, target: str = "CNY") -> str:
  """汇率换算，支持主要货币

  Args:
    amount: 金额
    source: 源货币代码(如USD/JPY/EUR/GBP/KRW)
    target: 目标货币代码(如CNY/USD)，默认人民币
  """
  source = source.upper().strip()
  target = target.upper().strip()
  try:
    client = get_client()
    resp = await client.get(
      f"https://api.exchangerate-api.com/v4/latest/{source}",
      timeout=10,
    )
    if resp.status_code != 200:
      return "汇率查询失败"
    data = resp.json()
    rates = data.get("rates", {})
    if target not in rates:
      return f"不支持的货币: {target}"
    rate = rates[target]
    result = amount * rate
    return f"{amount} {source} = {result:.2f} {target} (汇率: 1 {source} = {rate:.4f} {target})"
  except Exception as e:
    return f"汇率查询失败: {e}"


@tool(
  tags=["info"],
  examples=["怎么用Python写快排", "JS的Promise怎么用", "这段代码什么意思", "帮我写个正则"],
)
async def code_helper(ctx: ToolContext, question: str) -> str:
  """回答编程相关问题，支持代码解释、生成和调试

  Args:
    question: 编程问题
  """
  try:
    return await llm_complete(
      "你是编程助手。规则:\n- 回答简洁，代码不超过30行\n- 用中文解释，代码用英文\n- 如果是代码解释，先说功能再逐行说明\n- 不要废话，直接给答案",
      question,
      temperature=0.2,
      max_tokens=500,
      fallback="无法回答",
    )
  except Exception as e:
    return f"回答失败: {e}"
