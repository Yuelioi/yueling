"""确认机制 — 确认码 + 身份绑定 + 幂等保护 + 过期"""

import random
import string
import time
from dataclasses import dataclass, field


@dataclass
class PendingAction:
  action_id: str
  confirm_code: str
  user_id: int
  group_id: int
  tool_name: str
  tool_args: dict
  created_at: float = field(default_factory=time.time)
  expires_at: float = 0
  status: str = "pending"  # "pending" | "completed" | "expired"

  def __post_init__(self):
    if self.expires_at == 0:
      self.expires_at = self.created_at + 30.0

  @property
  def is_expired(self) -> bool:
    return time.time() > self.expires_at

  @property
  def is_active(self) -> bool:
    return self.status == "pending" and not self.is_expired


def _gen_code(length: int = 4) -> str:
  return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def _gen_id() -> str:
  return "".join(random.choices(string.hexdigits[:16], k=8))


class ConfirmManager:
  def __init__(self):
    self._pending: dict[str, PendingAction] = {}

  def create(self, user_id: int, group_id: int, tool_name: str, tool_args: dict) -> PendingAction:
    action = PendingAction(
      action_id=_gen_id(),
      confirm_code=_gen_code(),
      user_id=user_id,
      group_id=group_id,
      tool_name=tool_name,
      tool_args=tool_args,
    )
    self._pending[action.action_id] = action
    return action

  def try_confirm(self, user_id: int, group_id: int, text: str) -> PendingAction | None:
    text = text.strip().upper()
    for action in self._pending.values():
      if not action.is_active:
        continue
      if action.user_id != user_id or action.group_id != group_id:
        continue
      if action.confirm_code in text:
        action.status = "completed"
        return action
    return None

  def get_pending(self, user_id: int, group_id: int) -> PendingAction | None:
    for action in self._pending.values():
      if action.is_active and action.user_id == user_id and action.group_id == group_id:
        return action
    return None

  def cleanup_expired(self):
    expired = [k for k, a in self._pending.items() if a.is_expired or a.status != "pending"]
    for k in expired:
      del self._pending[k]

  def format_confirm_message(self, action: PendingAction) -> str:
    return (
      f"即将执行: {action.tool_name}\n"
      f"参数: {action.tool_args}\n"
      f"确认请回复: {action.confirm_code}\n"
      f"(30秒内有效，仅限本人)"
    )


confirm_manager = ConfirmManager()
