from nonebot_plugin_alconna import (
  Alconna,
  AlconnaMatcher,
  Args,
  At,
  Match,
  UniMessage,
  on_alconna,
)

test_cmd = on_alconna(Alconna("test", Args["target?", str | At]))


@test_cmd.handle()
async def tt_h(matcher: AlconnaMatcher, target: Match[str | At]):
  if target.available:
    matcher.set_path_arg("target", target.result)


# 参数引导, 满足参数自动进入, 不满足则提示(prompt)
@test_cmd.got_path("target", prompt="请输入目标")
async def tt(target: str | At):
  await test_cmd.send(UniMessage(["ok\n", target]))
