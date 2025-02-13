## 使用

修改 .env.example 为 .env, 填写对应配置, 不用的可以不填

下载 lgr, 进入文件夹 运行 ./Lagrange.OneBot

python bot.py 启动 bot

## 多平台

DISCORD 和开黑啦配置需要打开 bot.py , 删除前面的 `#`, 并且重启 bot

```python
# driver.register_adapter(DISCORD_ADAPTER)
# driver.register_adapter(KAIHEILA_ADAPTER)
```

[Tian-que/nonebot-adapter-kaiheila](https://github.com/Tian-que/nonebot-adapter-kaiheila)

[nonebot/adapter-discord](https://github.com/nonebot/adapter-discord)

## 资源

请下载资源包 data.zip 解压到机器人根目录

## 参考

框架: [https://nonebot.dev]()

协议: [LagrangeDev/Lagrange.Core](https://github.com/LagrangeDev/Lagrange.Core)
