from nonebot import require
from nonebot_plugin_alconna import (
  Alconna,
  Args,
  At,
  CommandMeta,
  Field,
  UniMsg,
  on_alconna,
)

require("nonebot_plugin_waiter")

from nonebot_plugin_waiter import waiter

alc = Alconna(
  "添加教师",
  Args["name", str, Field(completion=lambda: "请输入姓名")],
  Args["phone", int, Field(completion=lambda: "请输入手机号")],
  Args["at", [str, At], Field(completion=lambda: "请输入教师号")],
  meta=CommandMeta(context_style="parentheses"),
)

cmd = on_alconna(alc, comp_config={"lite": True}, skip_for_unmatch=False)


@cmd.handle()
async def handle(name: str, phone: int, at: str | At):
  # r = await UniMessage(f"姓名：{name}").send(reply_to=True)
  # await r.reply(f"手机号：{phone}")
  # await r.reply(f"教师号：{at!r}")
  # await r.recall(delay=5)

  await cmd.send("请回复验证码：")

  @waiter(["message"], keep_session=True)
  async def receive(msg: UniMsg):
    return msg

  async for res in receive(timeout=3):
    if not res:
      await cmd.send("超时")
      return
    if str(res) == "123456":
      await cmd.finish("验证成功")
      break
    await cmd.send("验证失败，请重新输入：")
    continue
