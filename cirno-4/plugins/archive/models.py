from pydantic import BaseModel
from sqlalchemy import Integer, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from nonebot import require

require("database_connector")
from ..database_connector import Base


# class Archive(Base):
#     __tablename__ = 'archive'
#     creator_id = Column('creator_id', MEDIUMTEXT)
#     create_name = Column('create_time', DATETIME, primary_key=True)
#     content = Column('content', TEXT)
#     is_private = Column('is_private', TINYINT)
#     creator = Column('creator', TEXT)
#     is_available = Column('is_available', TINYINT)
#     enabled_groups = Column('enabled_groups', TEXT)
#     keywords = Column('keywords', TEXT, primary_key=True)
#     alias = Column('alias', TEXT)
#     fuzzy_search = Column('fuzzy_search', TINYINT)
#     is_latest = Column('is_latest', TINYINT)
#     is_random = Column('is_random', TINYINT)


class EntryCache(BaseModel):
    key: str
    value: str
    available: int
    called_times: int
    creator_id: str
    creator_name: str
    type: str
    locked: int
    enabled_groups: list[str]


class Entry(Base):
    __tablename__ = 'entry'
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100))
    value = Column(String(5000))
    available = Column(Integer)
    called_times = Column(Integer)
    creator_id = Column(String(50))
    creator_name = Column(String(100))
    create_time = Column(DateTime)
    type = Column(String(50))
    locked = Column(Integer)
    # 一对多
    # 一个entry对应多个tag
    enabled_groups = relationship('Group', backref='entry')

    def to_cache(self) -> EntryCache:
        return EntryCache(
            key=self.key,
            value=self.value,
            available=self.available,
            called_times=self.called_times,
            creator_id=self.creator_id,
            creator_name=self.creator_name,
            type=self.type,
            locked=self.locked,
            enabled_groups=[group.group_id for group in self.enabled_groups]
        )


class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String(100))
    entry_id = Column(Integer, ForeignKey('entry.id'))