from nonebot import require

from sqlalchemy.future import select

from sqlalchemy import update

require("database_connector")

from ..database_connector import get_session
from .models import Archive

entries: list = []


async def fetch_all_entries() -> list:
    session = await get_session()
    async with session.begin():
        query = select(Archive)
        result = await session.execute(query)
        global entries
        entries = result.scalars().all()
        return entries


def get_entries():
    return entries


async def insert_new_entry(creator_id: int, content: str, keywords: str, enabled_groups: str, creator: str,
                           alias: str = None, fuzzy_search: int = 0,
                           is_private: int = 0,
                           is_available: int = 1,
                           is_random: int = 0):
    session = await get_session()
    async with session.begin():
        global entries
        add_entry = Archive(creator_id=creator_id, creator=creator, content=content, keywords=keywords, alias=alias,
                            fuzzy_search=fuzzy_search, is_private=is_private, is_available=is_available,
                            enabled_groups=enabled_groups, is_random=is_random, is_latest=True)
        for entry in entries:
            if entry.keywords == keywords and entry.enabled_groups == enabled_groups:
                entry.is_latest = 0
                entry.is_available = 0
        entries.append(add_entry)

        sql = update(Archive).where(Archive.keywords == keywords).where(Archive.enabled_groups == enabled_groups).values(
            is_latest=False, is_available=False)
        await session.execute(sql)
        session.add(add_entry)
        await session.commit()
