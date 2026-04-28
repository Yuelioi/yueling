from ai.registry import ToolMeta


SYSTEM_PROMPT = """你是月灵，一个QQ群助手机器人。
规则：
- 用户请求涉及具体操作时，必须调用工具，禁止编造结果
- 天气、搜索、翻译、计算、汇率等有对应工具的请求，必须调用工具，绝对不能用自己的知识回答
- 可以连续调用多个工具完成复杂任务（如先查聊天记录找到用户，再执行操作）
- 每一步使用上一步的结果作为输入
- 所有工具执行完后用简短文字总结结果
- 无法完成时直接说"我做不到这个"，不要瞎猜
- 回复简洁，不超过50字（除非用户要求详细或编程问答）
- 禁止暴露工具名称和内部逻辑
- 不确定时优先选择低风险工具
- 对模糊指令不要直接执行高危操作
- 如果消息中包含图片，优先考虑需要图片的工具

常见链式调用模式（可以连续调用多个工具）：
- 翻译图片文字: ocr_image → translate
- 查找并禁言: get_chat_history/resolve_user_by_name → ban_user
- 总结群聊: get_chat_history → summarize_chat
- 搜索并摘要: web_search → summarize_text"""


def build_tools_instruction(tools: list[ToolMeta]) -> str:
  lines = ["当用户请求涉及以下内容时调用对应工具："]
  for t in tools:
    lines.append(f"- {t.description} → {t.name}")

  neg_lines = []
  for t in tools:
    if t.negative_examples:
      neg_lines.append(f"\n不要在以下情况使用 {t.name}：")
      for neg in t.negative_examples:
        neg_lines.append(f"  - {neg}")

  if neg_lines:
    lines.append("")
    lines.extend(neg_lines)

  return "\n".join(lines)


def build_few_shot(tools: list[ToolMeta]) -> str:
  lines = ["以下是一些调用示例："]
  for t in tools:
    for ex in t.examples[:2]:
      lines.append(f"用户: {ex}\n→ 调用 {t.name}")
  return "\n".join(lines)


def build_context(user_role: str, tool_names: list[str], group_id: int, has_image: bool = False) -> str:
  ctx = f"""当前上下文：
用户权限: {user_role}
可用工具: {', '.join(tool_names)}
群号: {group_id}"""
  if has_image:
    ctx += "\n消息附带图片: 是（图片文字已通过OCR识别并附在消息中，请结合OCR内容回答用户问题）"
  return ctx


def build_system_message(
  tools: list[ToolMeta],
  user_role: str,
  group_id: int,
  has_image: bool = False,
  group_rules: list[str] | None = None,
) -> str:
  tool_names = [t.name for t in tools]
  parts = [
    SYSTEM_PROMPT,
    "",
    build_tools_instruction(tools),
    "",
    build_few_shot(tools),
    "",
    build_context(user_role, tool_names, group_id, has_image),
  ]
  if group_rules:
    parts.append("")
    parts.append("本群自定义规则（必须遵守）：")
    for rule in group_rules:
      parts.append(f"- {rule}")
  return "\n".join(parts)
