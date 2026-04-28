# 月灵 — QQ 群聊 AI Bot

基于 NoneBot2 + OneBot V11 的群聊机器人，具备 AI 自然语言调度、插件系统、好感度聊天等功能。

## 技术栈

- **框架**: NoneBot2 + OneBot V11 Adapter
- **AI**: DeepSeek (OpenAI SDK 兼容)
- **数据库**: SQLAlchemy 2.0 + aiosqlite (SQLite WAL)
- **Python**: 3.13+

## 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填写 API keys

# 3. 配置 bot
# 编辑 config.toml 设置 bot name, owner_id 等

# 4. 启动 OneBot 实现 (NapCat/Lagrange 等)

# 5. 启动 bot
python bot.py
```

## 项目结构

```
├── ai/              # AI 调度核心 (ReAct loop, tool registry, session)
├── core/            # 基础设施 (config, database, permissions, store)
├── models/          # SQLAlchemy ORM 模型
├── repositories/    # 数据访问层
├── services/        # 业务服务 (HTTP fetch, image, translate)
├── plugins/         # NoneBot 插件
│   ├── ai_dispatch/ # AI 自然语言调度入口
│   ├── funny/       # 娱乐 (复读, 运势, 热搜, 追番)
│   ├── game/        # 游戏 (PK, 剑网三)
│   ├── group/       # 群管 (禁言, 文件, 关键词)
│   ├── random/      # 随机 (roll, 每日, 图片)
│   ├── scheduler/   # 定时 (备忘录)
│   ├── system/      # 系统 (帮助, 插件管理, 图库)
│   ├── tools/       # 工具 (翻译, OCR, 计算器, 搜索)
│   └── user/        # 用户 (标签)
└── tests/           # 测试
```

## AI 系统

Bot 支持通过 @月灵 + 自然语言 来调用工具：

- 自动意图识别 + 工具分组
- ReAct 循环（最多 5 步重试）
- 权限前置检查
- 确认机制（高风险操作）
- 好感度聊天 fallback
- 每用户限流

## 开发

```bash
# 运行测试
uv run pytest tests/ -v

# 代码检查
uv run ruff check .

# 格式化
uv run ruff format .
```

## 插件开发

在 `plugins/` 下创建目录，定义 `__plugin_meta__`。如果需要接入 AI 调度，在 `extra["tools"]` 中声明工具：

```python
__plugin_meta__ = PluginMetadata(
  name="我的插件",
  description="描述",
  usage="用法",
  extra={
    "group": "分组",
    "commands": ["命令1"],
    "tools": [{
      "name": "my_tool",
      "description": "工具描述",
      "tags": ["tag1"],
      "handler": "do_my_tool",
    }],
  },
)
```

## 参考

- 框架: [NoneBot2](https://nonebot.dev)
- 协议实现: [NapCatQQ](https://github.com/NapNeko/NapCatQQ)

