from nonebot_plugin_alconna import Alconna, Args, Option, UniMessage, on_alconna

login = on_alconna(
  Alconna(
    "login",
    Args["password?", str],
    Option("out|--recall"),
  )
)
"""
登录/登出示例
login [密码?]: 登录, 密码可选
login out: 退出
login 密码 out: 也是退出,不过没人这样打!
"""


# 需匹配 --(recall)选项
@login.assign("recall")
async def login_exit():
  await login.finish("已退出")


@login.handle()
async def login_handle(password: str = ""):
  print(password)
  await login.send(UniMessage.template("{:At(user,$event.get_user_id())}, login success"))
