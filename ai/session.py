"""多轮会话管理 — 双层上下文隔离 + 弱引用 + TTL + 上下文压缩 + 可选持久化"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from nonebot import logger

SESSION_PERSIST_PATH = Path("data/sessions")
MAX_CONTEXT_TOKENS = 2000
KEEP_RECENT = 4


@dataclass
class Session:
  user_id: int
  group_id: int
  created_at: float = field(default_factory=time.time)
  ttl: float = 300.0  # 5分钟

  # 双层上下文隔离
  messages: list[dict] = field(default_factory=list)  # 喂给LLM的对话历史
  tool_state: dict = field(default_factory=dict)  # 结构化工具结果（不直接喂LLM）

  # 防循环
  used_tools: dict[str, int] = field(default_factory=dict)
  step_count: int = 0

  # 弱引用上下文（session过期后仍保留30min）
  last_meaningful_input: str = ""
  last_meaningful_at: float = 0

  @property
  def is_expired(self) -> bool:
    return time.time() - self.created_at > self.ttl

  def add_user_message(self, text: str):
    self.messages.append({"role": "user", "content": text})
    if len(text) > 5:
      self.last_meaningful_input = text
      self.last_meaningful_at = time.time()

  def add_assistant_message(self, text: str):
    self.messages.append({"role": "assistant", "content": text})

  def add_tool_result(self, tool_name: str, result: str):
    self.tool_state[tool_name] = result
    summary = result[:100] if len(result) > 100 else result
    self.messages.append({"role": "tool", "content": f"[{tool_name}]: {summary}"})

  def record_tool_use(self, tool_name: str):
    self.used_tools[tool_name] = self.used_tools.get(tool_name, 0) + 1
    self.step_count += 1

  def can_use_tool(self, tool_name: str, max_per_tool: int = 2) -> bool:
    return self.used_tools.get(tool_name, 0) < max_per_tool

  def get_context_messages(self) -> list[dict]:
    return [m for m in self.messages if m["role"] in ("user", "assistant")]

  @staticmethod
  def estimate_tokens(messages: list[dict]) -> int:
    return sum(len(m.get("content", "")) // 2 + 4 for m in messages)

  async def get_compressed_context(self) -> list[dict]:
    ctx_msgs = self.get_context_messages()
    if not ctx_msgs or self.estimate_tokens(ctx_msgs) <= MAX_CONTEXT_TOKENS:
      return ctx_msgs

    if len(ctx_msgs) <= KEEP_RECENT:
      return ctx_msgs

    old_msgs = ctx_msgs[:-KEEP_RECENT]
    recent_msgs = ctx_msgs[-KEEP_RECENT:]

    old_text = "\n".join(
      f"{'用户' if m['role'] == 'user' else '助手'}: {m['content']}"
      for m in old_msgs
    )

    try:
      from ai.llm import DEFAULT_MODEL, get_llm_client
      resp = await get_llm_client().chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
          {"role": "system", "content": "将以下对话记录压缩为简短摘要，保留关键信息、用户偏好和重要结论。100字以内。"},
          {"role": "user", "content": old_text},
        ],
        temperature=0.1,
        max_tokens=150,
      )
      summary = resp.choices[0].message.content or ""
    except Exception as e:
      logger.debug(f"Context compression failed: {e}")
      return recent_msgs

    compressed = [{"role": "system", "content": f"之前的对话摘要: {summary}"}]
    compressed.extend(recent_msgs)
    return compressed

  def to_dict(self) -> dict:
    return {
      "user_id": self.user_id,
      "group_id": self.group_id,
      "created_at": self.created_at,
      "last_meaningful_input": self.last_meaningful_input,
      "last_meaningful_at": self.last_meaningful_at,
      "messages": self.messages[-10:],
    }

  @classmethod
  def from_dict(cls, data: dict, ttl: float = 300.0) -> "Session":
    s = cls(
      user_id=data["user_id"],
      group_id=data["group_id"],
      created_at=data.get("created_at", time.time()),
      ttl=ttl,
    )
    s.last_meaningful_input = data.get("last_meaningful_input", "")
    s.last_meaningful_at = data.get("last_meaningful_at", 0)
    s.messages = data.get("messages", [])
    return s


class SessionManager:
  def __init__(self, ttl: float = 300.0, weak_ref_ttl: float = 1800.0, persist: bool = True):
    self._sessions: dict[str, Session] = {}
    self._ttl = ttl
    self._weak_ref_ttl = weak_ref_ttl
    self._persist = persist
    if persist:
      self._load_persisted()

  def _key(self, group_id: int, user_id: int) -> str:
    return f"{group_id}:{user_id}"

  def get(self, group_id: int, user_id: int) -> Session:
    key = self._key(group_id, user_id)
    session = self._sessions.get(key)

    if session and not session.is_expired:
      return session

    # 创建新 session，保留弱引用上下文
    new_session = Session(user_id=user_id, group_id=group_id, ttl=self._ttl)
    if session and (time.time() - session.last_meaningful_at < self._weak_ref_ttl):
      new_session.last_meaningful_input = session.last_meaningful_input
      new_session.last_meaningful_at = session.last_meaningful_at

    self._sessions[key] = new_session
    return new_session

  def clear(self, group_id: int, user_id: int):
    key = self._key(group_id, user_id)
    self._sessions.pop(key, None)

  def cleanup_expired(self):
    now = time.time()
    expired = [k for k, s in self._sessions.items() if now - s.created_at > self._ttl * 3]
    for k in expired:
      del self._sessions[k]

  def persist(self):
    if not self._persist:
      return
    SESSION_PERSIST_PATH.mkdir(parents=True, exist_ok=True)
    data = {}
    for key, session in self._sessions.items():
      if session.last_meaningful_input:
        data[key] = session.to_dict()
    try:
      path = SESSION_PERSIST_PATH / "active_sessions.json"
      path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
      logger.debug(f"Session persist failed: {e}")

  def _load_persisted(self):
    path = SESSION_PERSIST_PATH / "active_sessions.json"
    if not path.exists():
      return
    try:
      data = json.loads(path.read_text(encoding="utf-8"))
      now = time.time()
      for key, session_data in data.items():
        last_at = session_data.get("last_meaningful_at", 0)
        if now - last_at < self._weak_ref_ttl:
          self._sessions[key] = Session.from_dict(session_data, self._ttl)
    except Exception as e:
      logger.debug(f"Session load failed: {e}")


session_manager = SessionManager()
