"""群规则管理 — Procedural Memory 的管理入口"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata

from ai.memory import memory_manager
from core.permission import is_admin

__plugin_meta__ = PluginMetadata(
  name="群规则",
  description="管理群AI规则(Procedural Memory)",
  usage="群规则 添加/列表/删除",
  extra={"group": "群管", "commands": ["群规则"]},
)

rules_cmd = on_command("群规则")


@rules_cmd.handle()
async def handle_rules(bot: Bot, event: GroupMessageEvent):
  if not await is_admin(bot, event):
    await rules_cmd.finish("需要管理员权限")

  text = event.get_plaintext().strip()
  parts = text.split(maxsplit=2)
  if len(parts) < 2:
    await rules_cmd.finish("用法：群规则 添加/列表/删除 [内容/编号]")

  action = parts[1]

  if action == "列表":
    rules = await memory_manager.list_group_rules(event.group_id)
    if not rules:
      await rules_cmd.finish("本群暂无自定义规则")
    lines = ["本群AI规则："]
    for i, r in enumerate(rules, 1):
      lines.append(f"{i}. {r['rule']}")
    await rules_cmd.finish("\n".join(lines))

  elif action == "添加":
    if len(parts) < 3:
      await rules_cmd.finish("请输入规则内容：群规则 添加 <规则>")
    rule_text = parts[2].strip()
    if not rule_text:
      await rules_cmd.finish("规则内容不能为空")
    if len(rule_text) > 200:
      await rules_cmd.finish("规则内容不能超过200字")
    try:
      rule_id = await memory_manager.add_group_rule(event.group_id, rule_text, event.user_id)
      await rules_cmd.finish(f"规则已添加 (#{rule_id})")
    except ValueError as e:
      await rules_cmd.finish(str(e))

  elif action == "删除":
    if len(parts) < 3:
      await rules_cmd.finish("请输入规则编号：群规则 删除 <编号>")
    rules = await memory_manager.list_group_rules(event.group_id)
    try:
      idx = int(parts[2]) - 1
      if idx < 0 or idx >= len(rules):
        await rules_cmd.finish("编号不存在")
      rule_id = rules[idx]["id"]
      ok = await memory_manager.remove_group_rule(event.group_id, rule_id)
      if ok:
        await rules_cmd.finish("规则已删除")
      else:
        await rules_cmd.finish("删除失败")
    except ValueError:
      await rules_cmd.finish("请输入有效的数字编号")

  else:
    await rules_cmd.finish("未知操作，支持：添加/列表/删除")
