from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.message import event_preprocessor
from nonebot_plugin_alconna import Arparma, on_alconna

from common.Alc.Alc import arg

test = on_alconna(arg("测试"))

# input: 测试 111
# output: 你好


@event_preprocessor
async def do_something(event: GroupMessageEvent):
  msgs = event.get_message()
  for i, msg in enumerate(msgs):
    if msg.type == "text":
      msgs[i] = MessageSegment.text("你好")


@test.handle()
async def setu_h(result: Arparma, event: Event):
  print(result)  # 正常的原消息
  print(event.get_plaintext())  # 你好
