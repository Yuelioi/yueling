from datetime import date
from pathlib import Path

from plugins.funny.fortune.consts import FORTUNE_CACHE
from plugins.funny.fortune.utils import drawing


class FortuneManager:
  def divine(self, uid: str, theme: str):
    """
    今日运势抽签，主题已确认合法

    uid: 用户QQ号
    """
    today = date.today()
    img_path: Path = FORTUNE_CACHE / f"{uid}-{today}.png"
    for item in (FORTUNE_CACHE).iterdir():
      if f"{uid}-{today}" in item.name:
        return False, img_path
    try:
      img_path = drawing(uid, str(today), theme)
    except Exception:
      return True, None

    return True, img_path

  @staticmethod
  def clean_out_pics() -> None:
    """
    清空图片
    """
    for pic in FORTUNE_CACHE.iterdir():
      pic.unlink()


fortune_manager = FortuneManager()
