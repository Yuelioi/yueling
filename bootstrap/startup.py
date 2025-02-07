import shutil
from pathlib import Path

from common.config import config

# 创建配置文件
for key, value in config.resource.model_dump().items():
  Path(value).mkdir(parents=True, exist_ok=True)

# 清理tmp文件
for item in config.resource.tmp.iterdir():
  if item.is_dir():
    shutil.rmtree(item)
  else:
    item.unlink()
