from sqlalchemy import Column, Date, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from common.config.config import YUELING_DATA_FOLDER
from plugins.game.pk.const import REGISTER_MONEY, REGISTER_POWER

DBPath = YUELING_DATA_FOLDER / "pk" / "pk.db"


if not DBPath.exists():
  DBPath.parent.mkdir(parents=True, exist_ok=True)
  DBPath.touch()
engine = create_engine(f"sqlite:///{DBPath}")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
  __tablename__ = "users"
  id = Column(Integer, primary_key=True)
  user_id = Column(Integer, unique=True)
  nickname = Column(String, unique=True)
  power = Column(Integer, default=0)
  money = Column(Integer, default=0)


class Status(Base):
  __tablename__ = "status"
  id = Column(Integer, primary_key=True)
  user_id = Column(Integer)
  name = Column(String, unique=True)
  description = Column(String)
  duration = Column(Date)


class Buff(Base):
  __tablename__ = "buffs"
  id = Column(Integer, primary_key=True)
  user_id = Column(Integer)
  name = Column(String, unique=True)
  description = Column(String)
  duration = Column(Date)


class UserDB:
  def add_user(self, nickname, user_id) -> User:
    new_user = User(nickname=nickname, user_id=user_id, power=REGISTER_POWER, money=REGISTER_MONEY)
    session.add(new_user)
    session.commit()
    return new_user

  def get_user(self, user_id):
    user = session.query(User).filter(User.user_id == user_id).first()
    if not user:
      return self.add_user("无名氏_" + str(user_id), user_id)
    return user

  def get_all_users(self):
    return session.query(User).all()

  def add_money(self, user_id, money):
    user = self.get_user(user_id)
    user.money += money
    session.commit()

  def add_power(self, user_id, power):
    user = self.get_user(user_id)
    user.power += power
    session.commit()


class BuffDB: ...


# Create tables
Base.metadata.create_all(engine)


udb = UserDB()
bdb = BuffDB()
