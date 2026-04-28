"""QQ 平台专属 API"""

from services.http_fetch import fetch_image


async def download_avatar(user_id: int):
  url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
  return await fetch_image(url)
