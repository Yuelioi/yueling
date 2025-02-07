import json

from common.config import config

__fortune_data = config.resource.fortune
FORTUNE_CACHE = __fortune_data / "cache"
FORTUNE_THEMES = __fortune_data / "themes"
FORTUNE_COPYWRITING = __fortune_data / "copywriting.json"
FORTUNE_FONTS = __fortune_data / "fonts"


for folder in [FORTUNE_CACHE, FORTUNE_THEMES, FORTUNE_FONTS]:
  if not folder.exists():
    folder.mkdir(parents=True)

if not FORTUNE_COPYWRITING.exists():
  with open(FORTUNE_COPYWRITING, "w", encoding="utf-8") as f:
    json.dump(
      {
        "version": 1.2,
        "copywriting": [
          {"good-luck": "缺失数据", "rank": 27, "content": ["copywriting.json缺失！"]},
        ],
      },
      f,
      ensure_ascii=False,
      indent=2,
    )
