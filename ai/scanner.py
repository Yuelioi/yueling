"""
插件自动注册为 AI Tool 的机制。

插件只需在 __plugin_meta__.extra["tools"] 中声明工具定义即可：

```python
__plugin_meta__ = PluginMetadata(
  name="翻译",
  ...
  extra={
    "tools": [{
      "name": "translate",
      "description": "翻译文本到目标语言",
      "tags": ["language"],
      "examples": ["翻译 hello world", "把这段翻译成英文"],
      "parameters": {
        "text": {"type": "string", "description": "要翻译的文本"},
        "target_lang": {"type": "string", "description": "目标语言", "default": "zh"},
      },
      "handler": "translate_tool_handler",  # 模块内的 async 函数名
    }]
  },
)

async def translate_tool_handler(ctx: ToolContext, text: str, target_lang: str = "zh") -> str:
  ...
```
"""

from nonebot import get_loaded_plugins, logger

from ai.registry import ToolMeta, registry


def scan_plugins_for_tools():
  """扫描所有已加载的 NoneBot 插件，将声明了 tools 的注册到 AI registry"""
  for plugin in get_loaded_plugins():
    if not plugin.metadata or not plugin.metadata.extra:
      continue
    tools_config = plugin.metadata.extra.get("tools")
    if not tools_config:
      continue

    module = plugin.module
    if not module:
      continue

    for tool_def in tools_config:
      handler_name = tool_def.get("handler")
      if not handler_name:
        continue

      handler = getattr(module, handler_name, None)
      if not handler or not callable(handler):
        logger.warning(f"Tool handler '{handler_name}' not found in {plugin.name}")
        continue

      meta = ToolMeta(
        name=tool_def.get("name", handler_name),
        description=tool_def.get("description", ""),
        tags=tool_def.get("tags", []),
        examples=tool_def.get("examples", []),
        negative_examples=tool_def.get("negative_examples", []),
        parameters=tool_def.get("parameters", {}),
        permission=tool_def.get("permission", "member"),
        risk_level=tool_def.get("risk_level", "low"),
        confirm_required=tool_def.get("confirm_required", False),
        func=handler,
      )
      registry.register(meta)
      logger.info(f"Registered AI tool '{meta.name}' from plugin '{plugin.name}'")
