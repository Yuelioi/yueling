
import pytest

from core.database import Base, engine
from repositories.record_repo import RecordRepository
from repositories.reply_repo import ReplyRepository
from repositories.pk_repo import PkRepository


@pytest.fixture(autouse=True)
async def setup_db():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  yield
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def record_repo():
  return RecordRepository()


@pytest.fixture
def reply_repo():
  return ReplyRepository()


@pytest.fixture
def pk_repo():
  return PkRepository()


@pytest.mark.asyncio
async def test_clock_in(record_repo):
  success = await record_repo.clock_in(12345)
  assert success is True

  success_again = await record_repo.clock_in(12345)
  assert success_again is False


@pytest.mark.asyncio
async def test_reply_crud(reply_repo):
  added = await reply_repo.add(qq=100, keyword="hello", reply="world")
  assert added is True

  all_replies = await reply_repo.get_all()
  assert len(all_replies) == 1
  assert all_replies[0].keyword == "hello"

  deleted = await reply_repo.delete_by_id(all_replies[0].id)
  assert deleted is True

  all_replies = await reply_repo.get_all()
  assert len(all_replies) == 0


@pytest.mark.asyncio
async def test_pk_register(pk_repo):
  user = await pk_repo.register(user_id=999, nickname="test_user")
  assert user.power == 100
  assert user.money == 1000

  found = await pk_repo.get_user(999)
  assert found is not None
  assert found.nickname == "test_user"


@pytest.mark.asyncio
async def test_pk_update_power(pk_repo):
  await pk_repo.register(user_id=888, nickname="power_test")
  await pk_repo.update_power(888, -50)
  user = await pk_repo.get_user(888)
  assert user.power == 50
