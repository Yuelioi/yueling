
from sqlalchemy import func, select

from core.database import async_session
from models import PixivImage


class PixivRepository:

  async def get_random_by_score(self, min_score: int = 100, tag_jp: str | None = None, limit: int = 1) -> list[PixivImage]:
    async with async_session() as session:
      stmt = select(PixivImage).where(PixivImage.score >= min_score)
      if tag_jp:
        stmt = stmt.where(PixivImage.tags.contains([tag_jp]))
      stmt = stmt.order_by(func.random()).limit(limit)
      result = await session.execute(stmt)
      return list(result.scalars().all())

  async def get_by_id(self, image_id: int) -> PixivImage | None:
    async with async_session() as session:
      return await session.get(PixivImage, image_id)

  async def update_score(self, image_id: int, score: int) -> bool:
    async with async_session() as session:
      image = await session.get(PixivImage, image_id)
      if image:
        image.score = max(min(score, 100), -100)
        await session.commit()
        return True
      return False


pixiv_repo = PixivRepository()
