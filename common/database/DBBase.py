from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from time import time
from typing import Any

from nonebot import logger
from sqlalchemy import (
  Column,
  Connection,
  Engine,
  MetaData,
  Row,
  Table,
  create_engine,
)
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from common.models import Element


@dataclass
class DBManagerBase:
  db_path: str | Path
  table_name: str = ""
  debug: bool = False
  table_fields: list[Column] | None = None
  engine: Engine = field(init=False)
  metadata: MetaData = field(init=False)
  conn: Connection = field(init=False)
  table: Table = field(init=False)
  columns: list = field(default_factory=list)
  headers: list = field(init=False)

  def __post_init__(self):
    try:
      # Ensure the database file exists
      if not Path(self.db_path).exists():
        logger.opt(colors=True).info('<yellow>数据库不存在, 正在创建...</yellow> from <magenta>nonebot_plugin_yuelibot.base.DBBase</magenta>"')
        Path(self.db_path).touch()

      # Create the engine and establish a connection
      self.engine = create_engine(f"sqlite:///{self.db_path}", echo=self.debug)
      self.conn = self.engine.connect()
      self.metadata = MetaData()
      self.metadata.reflect(bind=self.engine)

    except Exception as e:
      logger.opt(colors=True).error(f'<red>数据库初始化失败...</red> {e} from <magenta>nonebot_plugin_yuelibot.base.DBBase</magenta>"')

    # Check and create table if necessary
    self._check_table()

    # Get table column headers
    self.headers = [column.name for column in self.table.c]

    self._after_init()

  def _check_table(self):
    """After connecting to the database, check for the table, and get or create it."""
    if self.table_name not in self._tables():
      self._create_table_fields()
      if self.table_fields:
        self.table = Table(self.table_name, self.metadata, *self.table_fields)
      else:
        self.table = Table(self.table_name, self.metadata)

      self.metadata.create_all(self.engine)
    else:
      self.table = Table(self.table_name, self.metadata, autoload_with=self.engine)

  def _after_init(self):
    """Operations to perform after initialization."""
    pass

  def _create_table_fields(self):
    """Create table fields before creating the table."""
    self.table_fields = []  # Define your table fields here

  def _close(self):
    """Close all connections."""
    if self.conn:
      self.conn.close()

    if self.engine:
      self.engine.dispose()

  def _drop_table(self):
    """Delete the table."""
    self.table.drop(self.engine)
    self._close()

  def _clear_data(self):
    """Clear the table data only."""
    delete_query = self.table.delete()
    self.conn.execute(delete_query)
    self.conn.commit()

  def _tables(self):
    """Return a list of table names in the database."""
    return list(self.metadata.tables.keys())

  def to_dict(self, result: Row[Any]):
    """Convert a single result to a dictionary."""
    return dict(zip(self.headers, result))

  def to_dicts(self, result: Sequence[Row[Any]]):
    """Convert multiple results to a list of dictionaries."""
    return [dict(zip(self.headers, row)) for row in result]

  def insert_data(self, element: Element, max_retries=3, delay=1) -> bool:
    """Insert a single element into the database."""
    for attempt in range(max_retries):
      try:
        self.conn.execute(self.table.insert().values(**asdict(element)))
        self.conn.commit()
        return True
      except OperationalError as e:
        if "database is locked" in str(e):
          logger.warning(f"Database is locked. Retrying ({attempt + 1}/{max_retries})...")
          time.sleep(delay)
        else:
          logger.error(f"Database operation failed: {e}")
          break
      except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error: {e}")
        break
    return False

  def insert_datas(self, elements: Sequence[Element], max_retries=3, delay=1) -> bool:
    """Insert multiple elements into the database."""
    retries = 0
    success = False
    while retries < max_retries:
      try:
        values = [asdict(element) for element in elements]
        self.conn.execute(self.table.insert(), values)
        self.conn.commit()
        success = True
        break
      except OperationalError as e:
        if "database is locked" in str(e):
          retries += 1
          logger.warning(f"Database is locked. Retrying ({retries}/{max_retries})...")
          time.sleep(delay)
        else:
          logger.error(f"Database operation failed: {e}")
          break
      except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error: {e}")
        break
    if not success:
      logger.error("Failed to insert data after multiple retries.")
    return success
