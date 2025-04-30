import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from nonebot import get_driver
from nonebot.adapters import Bot
from nonebot.log import logger
from tortoise import Tortoise

from common.config import config

driver = get_driver()

load_dotenv()

DB_PATH = os.getenv("DATABASE_URL")


# 创建配置文件
for key, value in config.resource.model_dump().items():
  Path(value).mkdir(parents=True, exist_ok=True)

# 清理tmp文件
for item in config.resource.tmp.iterdir():
  if item.is_dir():
    shutil.rmtree(item)
  else:
    item.unlink()


@driver.on_bot_connect
async def _bot_connect(bot: Bot):
  await Tortoise.init(
    db_url=DB_PATH,
    modules={"models": ["common.models.ba"]},
  )
  logger.info("postgresql connect")


@driver.on_bot_disconnect
async def _bot_disconnect():
  await Tortoise.close_connections()
