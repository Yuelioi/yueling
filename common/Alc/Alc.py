from io import BytesIO
from pathlib import Path
from typing import Any, cast

from arclet.alconna import AllParam
from nonebot import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_Handler
from nonebot_plugin_alconna import (
  Alconna,
  AlconnaMatcher,
  Args,
  CommandMeta,
  MultiVar,
  UniMessage,
)


def pm(name: str, description: str, usage: str, group: str, hidden: bool = False):
  extra = {"group": group, "hidden": hidden}
  return PluginMetadata(name=name, description=description, usage=usage, extra=extra)


def ptc(p: PluginMetadata, compact: bool = True) -> CommandMeta:
  c = CommandMeta()
  c.description = p.description
  c.usage = p.usage
  c.extra = p.extra
  c.extra.setdefault("name", p.name)
  c.extra.setdefault("hidden", p.extra.get("hidden", False))
  c.extra.setdefault("group", p.extra.get("group", "未命名"))
  c.compact = compact

  return c


def msg():
  """
  匹配所有消息
  接受参数 result: Arparma cmds:Any(uni msg)

  全部: result.origin
  命令头: result.header_match.result
  命令: cmds

  需要使用meta ptc
  """

  return Alconna("re:.+", Args["args?", MultiVar(Any, "*")])


def fullmatch(
  command: str,
):
  """
  完全匹配 = on_fullmatch

  """
  return Alconna(command)


def multi_args(command: str, *args: tuple[str, type, int] | tuple[str, type] | tuple[type] | tuple[str]):
  """
  处理多个命令组，每个命令组由 name 和 type 组成。

  参数:
  tuple[str]: 命名多值, 类型都是str
  tuple[type]: 类型多值, 命名为 arg1,arg2...
  tuple[str, type]:正常命名 name:type
  tuple[str, type, int]: MultiVar
  """
  _args = Args()

  for index, arg in enumerate(args):
    if (len(arg)) == 1:
      if isinstance(arg[0], type):
        _args.add(name="arg" + str(index + 1), value=arg[0])
      else:
        _args.add(name=arg[0], value=str)
    else:
      # 多值
      if len(arg) == 3:
        name, _type, count = arg
        _args.add(name=name, value=MultiVar(_type, count))
      else:
        name, _type = arg
        _args.add(name=name, value=_type)

  return Alconna(command, _args)


def args(command: str, arg_limit: int = 99, type: type = str, required=True, meta: CommandMeta | None = None):
  """
  多参数
  type: 手动指定类型, 默认str
  arg_require: 需要参数
  arg_limit: 参数个数

  接收参数 args:list[type] = []
  """
  if required:
    return Alconna(command, Args["args", MultiVar(type, arg_limit)], meta=meta)
  return Alconna(command, Args["args?", MultiVar(type, arg_limit)], meta=meta)


def arg(command: str, type: type = str, required=True, meta: CommandMeta | None = None):
  """
  单参数
  type: 手动指定类型, 默认str

  接收参数
  arg:type       必传
  arg:type = ""  可选
  """
  if required:
    return Alconna(command, Args["arg", type], meta=meta)
  return Alconna(command, Args["arg?", type], meta=meta)


def res_handle(dependency: T_Handler | None = None):
  """
  一个结果处理器，用于处理命令返回值。

  原始用法:
  @cmd.handler()
  async def foo(arg: str):
    await cmd.finish(arg)

  现在用法
  async def foo(arg: str):
    return arg
  cmd.append_handler(res_handle())
  """

  async def handle(
    matcher: Matcher,
    res=Depends(dependency),
  ):
    if res is None or not res:
      return
    try:
      alcMatcher = cast(AlconnaMatcher, matcher)
      if isinstance(res, BytesIO) or isinstance(res, bytes):
        await alcMatcher.finish(UniMessage.image(raw=res))
        UniMessage.image(raw=res)
      elif isinstance(res, Path):
        await alcMatcher.finish(UniMessage.image(path=res))
      elif isinstance(res, MessageSegment):
        await alcMatcher.finish(res)
      elif isinstance(res, Message):
        await alcMatcher.finish(res)

      await alcMatcher.finish(res)
    except FinishedException:
      return
    except Exception as e:
      logger.error("发送失败", res, e)

    return

  return handle


def register_handler(matcher: type[AlconnaMatcher | Matcher], dependency: T_Handler | None = None):
  matcher.append_handler(res_handle(dependency))
