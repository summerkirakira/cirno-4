from sqlalchemy import Integer, Column
from sqlalchemy.dialects.mysql import MEDIUMTEXT, DATETIME, TEXT, TINYINT
from sqlalchemy.orm import declarative_base
from nonebot import require

require("database_connector")

from ..database_connector import Base


class Archive(Base):
    __tablename__ = 'archive'
    creator_id = Column('creator_id', MEDIUMTEXT)
    create_name = Column('create_time', DATETIME, primary_key=True)
    content = Column('content', TEXT)
    is_private = Column('is_private', TINYINT)
    creator = Column('creator', TEXT)
    is_available = Column('is_available', TINYINT)
    enabled_groups = Column('enabled_groups', TEXT)
    keywords = Column('keywords', TEXT, primary_key=True)
    alias = Column('alias', TEXT)
    fuzzy_search = Column('fuzzy_search', TINYINT)
    is_latest = Column('is_latest', TINYINT)
    is_random = Column('is_random', TINYINT)

