"""AI 调度核心 — ReAct 状态机 + 权限前置 + 工具分组 + 校验回注"""

import asyncio
import json

from nonebot import logger

from ai.confirm import confirm_manager
from ai.executor import execute_tool
from ai.llm import DEFAULT_MODEL, get_llm_client
from ai.memory import memory_manager, should_store_episode, should_write_semantic
from ai.prompt import build_system_message
from ai.rate_limit import rate_limiter
from ai.registry import ToolMeta, registry
from ai.session import session_manager
from ai.trace import record_trace
from core import store
from core.context import ToolContext
from core.permission import permission_manager

MAX_STEPS = 5

# ─── 工具分组：意图关键词 → tag 映射 ─────────────────────────

INTENT_TAG_MAP = {
  "翻译": ["language"],
  "图": ["image", "fun"],
  "图片": ["image", "fun"],
  "头像": ["context", "image"],
  "管理": ["moderation", "group"],
  "热搜": ["search", "info"],
  "搜": ["search", "web"],
  "搜索": ["search", "web"],
  "随机": ["fun", "random"],
  "roll": ["fun", "random"],
  "识别": ["image", "ocr"],
  "运势": ["fun"],
  "计算": ["math"],
  "提醒": ["scheduler"],
  "游戏": ["game"],
  "物价": ["game"],
  "聊天记录": ["context"],
  "刚才": ["context"],
  "谁": ["context", "group"],
  "群友": ["context", "group"],
  "成员": ["context", "group"],
  "天气": ["info", "web"],
  "气温": ["info", "web"],
  "机票": ["travel"],
  "航班": ["travel"],
  "火车": ["travel"],
  "高铁": ["travel"],
  "车票": ["travel"],
  "好感": ["context"],
  "关系": ["context"],
  "喜欢我": ["context"],
  "文件": ["group", "search"],
  "吃": ["fun", "random"],
  "喝": ["fun", "random"],
  "玩": ["fun", "random"],
  "水果": ["fun", "random"],
  "标签": ["context"],
  "总结": ["context", "language"],
  "摘要": ["context", "language"],
  "聊了什么": ["context"],
  "在聊啥": ["context"],
  "活跃": ["context", "group"],
  "话最多": ["context", "group"],
  "汇率": ["math", "info"],
  "美元": ["math", "info"],
  "日元": ["math", "info"],
  "欧元": ["math", "info"],
  "韩元": ["math", "info"],
  "换算": ["math", "info"],
  "代码": ["info"],
  "编程": ["info"],
  "写个": ["info"],
  "正则": ["info"],
  "Python": ["info"],
  "JS": ["info"],
  "Java": ["info"],
  "禁用": ["moderation", "group"],
  "启用": ["moderation", "group"],
  "插件": ["moderation", "group"],
  "缩写": ["language", "info"],
  "什么意思": ["language", "info"],
  "yyds": ["language", "info"],
  "诗": ["fun"],
  "鸡汤": ["fun"],
  "热评": ["fun"],
  "来首": ["fun"],
  "Epic": ["info"],
  "免费游戏": ["info"],
  "白嫖": ["info"],
  "待办": ["info"],
  "记一下": ["info"],
  "todo": ["info"],
  "点歌": ["fun", "search"],
  "歌": ["fun", "search"],
  "搜图": ["image", "search"],
  "出处": ["image", "search"],
  "图源": ["image", "search"],
  "距离": ["math", "info"],
  "倒计时": ["math", "info"],
  "天后": ["math", "info"],
  "星期": ["math", "info"],
  "IP": ["info"],
  "ip": ["info"],
  "归属": ["info"],
  "人设": ["fun"],
  "帮我选": ["fun"],
  "选择困难": ["fun"],
  "排行": ["context", "group"],
  "排名": ["context", "group"],
  "匿名": ["fun"],
  "表白": ["fun"],
  "吐槽": ["fun"],
  "星座": ["fun", "info"],
  "运势": ["fun", "info"],
  "白羊": ["fun", "info"],
  "金牛": ["fun", "info"],
  "双子": ["fun", "info"],
  "巨蟹": ["fun", "info"],
  "狮子": ["fun", "info"],
  "处女": ["fun", "info"],
  "天秤": ["fun", "info"],
  "天蝎": ["fun", "info"],
  "射手": ["fun", "info"],
  "摩羯": ["fun", "info"],
  "水瓶": ["fun", "info"],
  "双鱼": ["fun", "info"],
  "接龙": ["fun", "language"],
  "成语": ["fun", "language"],
  "老黄历": ["fun"],
  "宜忌": ["fun"],
  "适合做": ["fun"],
}


# ─── 权限过滤 ────────────────────────────────────────────────

def get_available_tools(user_role: str, group_id: int = 0, user_id: int = 0) -> list[ToolMeta]:
  banned = set(store.group_blacklist.get(group_id, [])) if group_id else set()
  available = []
  for t in registry.get_all():
    if t.permission == "admin" and user_role not in ("admin", "owner", "superuser"):
      continue
    if t.permission == "superuser" and user_role != "superuser":
      continue
    if t.plugin_name and t.plugin_name in banned:
      continue
    if t.plugin_name and user_id and permission_manager.is_user_blocked(t.plugin_name, user_id):
      continue
    available.append(t)
  return available


def select_candidate_tools(text: str, available: list[ToolMeta], step: int = 0) -> list[ToolMeta]:
  max_tools = 15

  matched_tags: set[str] = set()
  for keyword, tags in INTENT_TAG_MAP.items():
    if keyword in text:
      matched_tags.update(tags)

  if matched_tags:
    candidates = [t for t in available if set(t.tags) & matched_tags]
    if candidates:
      return candidates[:max_tools]

  return available[:max_tools]


# ─── ReAct 状态机 ────────────────────────────────────────────


def _fire_memory_extraction(user_id: int, text: str, reply: str):
  if not should_write_semantic(text):
    return
  asyncio.create_task(
    memory_manager.smart_write_semantic(user_id, text, reply)
  )


async def dispatch(text: str, ctx: ToolContext) -> str:
  if not rate_limiter.is_allowed(ctx.user_id, ctx.group_id):
    return "你问得太快了，请稍后再试~"

  available = get_available_tools(ctx.role, ctx.group_id, ctx.user_id)
  if not available:
    return "当前没有可用的工具"

  session = session_manager.get(ctx.group_id, ctx.user_id)

  # 检查是否是确认回复
  if pending := confirm_manager.try_confirm(ctx.user_id, ctx.group_id, text):
    result = await execute_tool(pending.tool_name, pending.tool_args, ctx)
    record_trace(text, pending.tool_name, pending.tool_args, result, session.step_count)
    return result.replace("ERROR:", "执行失败: ") if result.startswith("ERROR:") else result

  session.add_user_message(text)
  images = ctx.get_images()
  has_image = bool(images)

  if has_image:
    from plugins.tools.ocr import do_ocr
    ocr_parts = []
    for img_url in images[:3]:
      try:
        ocr_text = await do_ocr(img_url)
        if ocr_text and ocr_text != "未识别出文字":
          ocr_parts.append(ocr_text)
      except Exception:
        pass
    if ocr_parts:
      session.add_user_message("图片中识别到的文字：\n" + "\n---\n".join(ocr_parts))

  candidates = select_candidate_tools(text, available, session.step_count)

  # 获取群规则
  group_rules: list[str] = []
  try:
    group_rules = await memory_manager.get_group_rules(ctx.group_id)
  except Exception:
    pass

  system_msg = build_system_message(candidates, ctx.role, ctx.group_id, has_image, group_rules)
  tools_schema = [t.to_openai_schema() for t in candidates]

  # 构建 messages：system + memory context + session历史 + 当前
  messages = [{"role": "system", "content": system_msg}]

  try:
    user_context = await memory_manager.get_user_context(ctx.user_id)
    if user_context:
      messages.append({"role": "system", "content": user_context})
  except Exception:
    pass

  if session.last_meaningful_input and session.step_count == 0:
    messages.append({"role": "system", "content": f"上一次对话上下文: {session.last_meaningful_input}"})
  messages.extend(await session.get_compressed_context())

  # ─── ReAct Loop ──────────────────────────────────────────
  for step in range(MAX_STEPS):
    try:
      response = await get_llm_client().chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        tools=tools_schema if tools_schema else None,
        temperature=0.3,
        max_tokens=300,
      )
    except Exception as e:
      logger.error(f"AI dispatch LLM error: {e}")
      return "AI 服务暂时不可用"

    choice = response.choices[0]

    # ─── 无工具调用 ──────────────────────────────────────────
    if not choice.message.tool_calls:
      if step > 0:
        # 链式调用结束，LLM 用文本总结最终结果
        reply = choice.message.content or "执行完成"
        session.add_assistant_message(reply)
        record_trace(text, None, {}, reply, step)

        if should_store_episode(None, step, True):
          try:
            await memory_manager.write_episodic(
              user_id=ctx.user_id, group_id=ctx.group_id,
              input_text=text, tool_name="chain",
              tool_args=json.dumps({"steps": step}, ensure_ascii=False),
              result_summary=reply[:100], steps=step,
            )
          except Exception:
            pass
        _fire_memory_extraction(ctx.user_id, text, reply)
        return reply
      # 第一轮就没选工具 → fallback 到好感度聊天
      from ai.chat import chat_fallback
      reply = await chat_fallback(text, ctx.bot, ctx.event)
      session.add_assistant_message(reply)
      record_trace(text, None, {}, reply, step)
      _fire_memory_extraction(ctx.user_id, text, reply)
      return reply

    # ─── 有工具调用 → 执行 ────────────────────────────────
    tool_call = choice.message.tool_calls[0]
    tool_name = tool_call.function.name
    try:
      tool_args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
      tool_args = {}

    # 防循环检查
    if not session.can_use_tool(tool_name):
      messages.append(choice.message.model_dump())
      messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": f"工具 {tool_name} 已达到调用上限"})
      continue

    # 确认机制检查
    meta = registry.get_by_name(tool_name)
    if meta and meta.confirm_required:
      action = confirm_manager.create(ctx.user_id, ctx.group_id, tool_name, tool_args)
      record_trace(text, tool_name, tool_args, "CONFIRM_REQUIRED", step)
      return confirm_manager.format_confirm_message(action)

    # 执行工具
    session.record_tool_use(tool_name)

    if step > 0:
      tool_desc = meta.description if meta else tool_name
      try:
        await ctx.bot.send(ctx.event, f"💭 {tool_desc}...")
      except Exception:
        pass

    result = await execute_tool(tool_name, tool_args, ctx)

    # 校验失败 → 回注LLM重试
    if result.startswith("ERROR:"):
      messages.append(choice.message.model_dump())
      messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
      # 动态收缩工具列表
      candidates = select_candidate_tools(text, available, step + 1)
      tools_schema = [t.to_openai_schema() for t in candidates]
      continue

    # 成功 → 回注结果，让 LLM 决定是否继续调用下一个工具
    session.add_tool_result(tool_name, result)
    messages.append(choice.message.model_dump())
    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

    # 最后一步了，直接返回
    if step == MAX_STEPS - 1:
      record_trace(text, tool_name, tool_args, result, step)
      session.add_assistant_message(result)
      _fire_memory_extraction(ctx.user_id, text, result)
      return result

    # 刷新候选工具列表（后续步骤可能需要不同的工具）
    candidates = select_candidate_tools(text, available, step + 1)
    tools_schema = [t.to_openai_schema() for t in candidates]

  # 循环结束后不应到这里，但兜底
  # 取最后一次工具结果作为返回
  last_result = ""
  for msg in reversed(messages):
    if msg.get("role") == "tool":
      last_result = msg.get("content", "")
      break
  if last_result:
    record_trace(text, None, {}, last_result, MAX_STEPS)
    session.add_assistant_message(last_result)
    _fire_memory_extraction(ctx.user_id, text, last_result)

    if should_store_episode(None, MAX_STEPS, True):
      pass
    return last_result

  return "处理步骤过多，请简化你的请求"
