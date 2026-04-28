"""月灵异常体系 — 分层错误处理"""


class BotError(Exception):
  """所有业务异常的基类"""

  def __init__(self, message: str = "操作失败"):
    self.message = message
    super().__init__(message)

  def user_message(self) -> str:
    return self.message


class InvalidInput(BotError):
  """用户输入校验失败 — 参数不合法、找不到用户等"""
  pass


class PermissionDenied(BotError):
  """权限不足"""

  def __init__(self, message: str = "权限不足，无法执行此操作"):
    super().__init__(message)


class ToolExecutionError(BotError):
  """工具执行异常 — API 调用失败、内部逻辑错误等"""

  def __init__(self, tool_name: str, message: str = "工具执行失败"):
    self.tool_name = tool_name
    super().__init__(f"{tool_name}: {message}")


class ExternalServiceError(BotError):
  """外部服务不可用 — HTTP 超时、第三方 API 异常等"""

  def __init__(self, service: str, message: str = "服务暂时不可用"):
    self.service = service
    super().__init__(f"{service} {message}")


class RateLimited(BotError):
  """触发限流"""

  def __init__(self, message: str = "请求过于频繁，请稍后再试"):
    super().__init__(message)


class SessionExpired(BotError):
  """会话过期"""

  def __init__(self, message: str = "会话已过期，请重新发起"):
    super().__init__(message)
