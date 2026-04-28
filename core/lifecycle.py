import shutil
from pathlib import Path

from nonebot import get_driver
from nonebot.log import logger

from core.config import config
from core.database import init_db, close_db

driver = get_driver()


@driver.on_startup
async def startup():
  for key, value in config.paths.model_dump().items():
    Path(value).mkdir(parents=True, exist_ok=True)

  if config.paths.tmp.exists():
    for item in config.paths.tmp.iterdir():
      if item.is_dir():
        shutil.rmtree(item)
      else:
        item.unlink()

  import models  # noqa: F401
  import ai.memory  # noqa: F401
  await init_db()
  logger.info("Database initialized")


@driver.on_shutdown
async def shutdown():
  from ai.session import session_manager
  session_manager.persist()
  await close_db()
