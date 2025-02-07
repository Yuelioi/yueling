from nonebot_plugin_alconna import Alconna, AlconnaArg, Args, Match, Option, on_alconna

group = on_alconna(
  Alconna(
    "group",
    Option("add", Args["group_id", int]["name?", str]),
    Option("remove", Args["group_id", int]),
    Option("list"),
  ),
)


def permission_checker(permission: str):
  import random

  async def wrapper(event, bot, state, arp):
    if random.random() < 0.5:
      await bot.send(event, "permission denied")
      return False
    return True

  return wrapper


@group.assign("add", additional=permission_checker("group.add"))
async def group_add(name: Match[str]):
  if name.available:
    group.set_path_arg("add.name", name.result)


@group.got_path("add.name", prompt="请输入群名")
async def group_add_name(group_id: int, name: str = AlconnaArg("add.name")):
  await group.finish(f"add {group_id} {name}")


@group.assign("remove", additional=permission_checker("group.remove"))
async def group_remove(group_id: int):
  await group.finish(f"remove {group_id}")


@group.assign("list")
async def group_list():
  await group.finish("list")
