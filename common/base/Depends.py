import re

from nonebot.params import Depends
from nonebot.typing import T_State


def extract_qq_numbers(input_string):
  # 使用正则表达式查找连续的1到12位数字
  continuous_numbers = re.findall(r"\d{1,12}", input_string)
  number_list = [int(num) for num in continuous_numbers]
  return number_list


def UserImgs(min_num: int = 1, max_num: int = 1):
  """用户图片链接"""

  async def dependency(state: T_State):
    imgs = state.get("imgs", [])
    if len(imgs) > max_num or len(imgs) < min_num or len(imgs) == 0:
      return
    return imgs

  return Depends(dependency)


def UserImg():
  """单张图片链接"""

  async def dependency(state: T_State):
    imgs = state.get("imgs", [])
    if len(imgs) > 0:
      return imgs[0]
    return imgs

  return Depends(dependency)


def Users(min_num: int = 1, max_num: int = 1):
  """用户信息(多个) 只提取1~12位数字"""

  async def dependency(state: T_State, ats=Ats(0, 99)):
    if args := state.get("_prefix", {}).get("command_arg"):
      args = args.extract_plain_text().strip().split()
      if ats:
        args.extend(str(at.get("user_id")) for at in ats)
      if len(args) <= max_num and len(args) >= min_num:
        return extract_qq_numbers(" ".join(args))
    return

  return Depends(dependency)


def User():
  """用户信息(一个) 只提取1~12位数字"""

  async def dependency(state: T_State, ats=Ats(0, 99)):
    if args := state.get("_prefix", {}).get("command_arg"):
      args = args.extract_plain_text().strip().split()
      if ats:
        args.extend(str(at.get("user_id")) for at in ats)
      if args:
        return extract_qq_numbers(" ".join(args))[0]
    return

  return Depends(dependency)


def Args(min_num: int = 1, max_num: int = 1):
  """提取多个参数 以空格或者回车分割"""

  async def dependency(state: T_State):  # -> list[Any] | Any | None:# -> list[Any] | Any | None:
    if args := state.get("_prefix", {}).get("command_arg"):
      command: str = args.extract_plain_text()
      args = command.strip().split()
      if len(args) > max_num or len(args) < min_num:
        return False
      return args
    return False

  return Depends(dependency)


def Arg():
  async def dependency(state: T_State):
    args = await Args()(state)
    if args:
      return args[0]
    return False

  return Depends(dependency)


def Ats(min_num: int = 1, max_num: int = 1):
  async def dependency(state: T_State):
    args = state.get("ats", [])
    if len(args) > max_num or len(args) < min_num or len(args) == 0:
      return
    return args

  return Depends(dependency)


def At():
  async def dependency(state: T_State):
    args = state.get("ats", [])
    if len(args) > 0:
      return args[0]
    return args

  return Depends(dependency)


Number = User
Numbers = Users
