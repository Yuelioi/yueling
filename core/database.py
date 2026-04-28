from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core.config import config

db_path = Path(config.db.path)
db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(
  f"sqlite+aiosqlite:///{db_path}",
  echo=False,
)


@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
  cursor = dbapi_conn.cursor()
  cursor.execute("PRAGMA journal_mode=WAL")
  cursor.execute("PRAGMA foreign_keys=ON")
  cursor.close()


async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
  pass


async def init_db():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)


async def close_db():
  await engine.dispose()
