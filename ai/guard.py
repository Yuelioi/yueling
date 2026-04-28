"""安全守卫 — 关键词 + 模式匹配两层拦截"""

import re

HIGH_RISK_KEYWORDS = {"禁言", "ban", "mute", "踢", "kick", "踢出", "管理", "重启", "reboot", "删除群文件"}

MODERATION_HINTS = {"处理", "教训", "惩罚", "收拾", "治", "制裁", "冷静", "整", "消失", "闭嘴", "说不了话"}

HIGH_RISK_PATTERNS = [
  re.compile(r"禁.*言|ban|mute|kick|踢.*出?|解禁", re.IGNORECASE),
  re.compile(r"重启|reboot|shutdown|关机"),
  re.compile(r"删除.*(文件|消息|记录)|清空"),
  re.compile(r"全[群体].*禁|禁.*全[群体]"),
]

INJECTION_PATTERNS = [
  re.compile(r"忽略.*(指令|规则|限制|提示)", re.IGNORECASE),
  re.compile(r"(system|系统).*(prompt|提示|指令)", re.IGNORECASE),
  re.compile(r"(无视|忘记|丢弃).*(之前|上面|所有).*(指令|规则)", re.IGNORECASE),
  re.compile(r"你(现在|从现在)是", re.IGNORECASE),
  re.compile(r"(DAN|jailbreak|越狱).*模式", re.IGNORECASE),
  re.compile(r"\[?(SYSTEM|系统)\]?\s*:?\s*(override|覆盖|新指令)", re.IGNORECASE),
  re.compile(r"(复述|重复|输出|告诉).*(system|系统|初始).*(prompt|提示|指令)", re.IGNORECASE),
  re.compile(r"(list|列出|显示).*(tool|工具|function|函数)", re.IGNORECASE),
]

PRIVILEGE_ESCALATION_PATTERNS = [
  re.compile(r"(设|给|提升).*(管理|admin|超级|权限)"),
  re.compile(r"(我是|我现在是).*(管理|admin|超级)"),
]


def guard_check(text: str, user_role: str) -> str | None:
  text_lower = text.lower()

  for pattern in INJECTION_PATTERNS:
    if pattern.search(text):
      return "检测到异常指令，已拒绝"

  for pattern in PRIVILEGE_ESCALATION_PATTERNS:
    if pattern.search(text):
      return "无法执行权限变更操作"

  for kw in HIGH_RISK_KEYWORDS:
    if kw in text_lower:
      if user_role not in ("admin", "owner", "superuser"):
        return "权限不足，该操作需要管理员权限"
      return None

  for pattern in HIGH_RISK_PATTERNS:
    if pattern.search(text):
      if user_role not in ("admin", "owner", "superuser"):
        return "权限不足，该操作需要管理员权限"
      return None

  hint_count = sum(1 for h in MODERATION_HINTS if h in text_lower)
  if hint_count >= 1 and user_role not in ("admin", "owner", "superuser"):
    return "检测到可能的管理操作意图，权限不足"

  return None
