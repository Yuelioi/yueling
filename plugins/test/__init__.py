from typing import Any

from nonebot.adapters import Event
from nonebot_plugin_alconna import (
  AlcMatches,
  Alconna,
  Args,
  Arparma,
  Image,
  MultiVar,
  Reply,
  UniMsg,
  on_alconna,
)
from nonebot_plugin_alconna.builtins.extensions import ReplyRecordExtension
from nonebot_plugin_alconna.builtins.extensions.reply import ReplyMergeExtension

_test = Alconna("测试", Args["img", MultiVar(Image, "*")])
test = on_alconna(_test, extensions=[ReplyMergeExtension()])


@test.handle()
async def setu_h(msg: UniMsg, am: AlcMatches):
  # await test.finish("干什么!")
  print(am)
  print(msg)
  if msg.has(Image):
    print("work")

    imgs = msg.get(Image)
    for img in imgs:
      print(img.url)
  # res = f"""
  #   origin: {result.origin}
  #   matched: {result. matched}
  #   header_match: {result.header_match}
  #   main_args: {result.main_args}
  #   other_args: {result.other_args}
  #   options: {result. options}
  #   subcommands: {result. subcommands}
  #   head result: {result.header_result}
  #   args: {result.all_matched_args}
  #   """

  # print(res)
