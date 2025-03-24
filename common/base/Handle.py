from io import BytesIO
from pathlib import Path
from typing import Callable

from nonebot import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.typing import T_Handler


def res_handle(dependency: T_Handler | None = None):
  async def handle(
    matcher: Matcher,
    res=Depends(dependency),
  ):
    if res is None or not res:
      return
    try:
      if isinstance(res, BytesIO) or isinstance(res, bytes) or isinstance(res, Path):
        await matcher.finish(MessageSegment.image(file=res))
      elif isinstance(res, MessageSegment):
        await matcher.finish(res)
      elif isinstance(res, Message):
        await matcher.finish(res)

      await matcher.finish(res)
    except FinishedException:
      return
    except Exception as e:
      logger.error("发送失败", res, e)

    return

  return handle


def register_handler(matcher: type[Matcher], func: Callable):
  matcher.append_handler(res_handle(func))
