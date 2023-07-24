from typing import Optional, Union

from nonebot import require, logger, get_driver, on_command

from sqlalchemy.future import select

from sqlalchemy import update, delete, insert, or_
from pathlib import Path

from sqlalchemy.orm import selectinload

require("database_connector")

import httpx

from ..database_connector import get_session
from .models import Entry, Group, EntryCache, Alias

entries: list[EntryCache] = []

qq_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Host': 'gchat.qpic.cn'
}

driver = get_driver()


async def fetch_all_entries() -> list[Entry]:
    session = await get_session()
    async with session.begin():
        result = await session.execute(select(Entry)
                                       .options(selectinload(Entry.enabled_groups))
                                       .options(selectinload(Entry.aliases)))
        global entries
        entries = [cache.to_cache() for cache in result.scalars().all()]
        return entries


@driver.on_startup
async def init_entries():
    await fetch_all_entries()


def get_entry(key: str, sender_id: str, group_id: str) -> Optional[EntryCache]:
    for entry in entries:
        if entry.key == key or key in entry.aliases:
            if group_id in entry.enabled_groups or "0" in entry.enabled_groups:
                return entry
            if entry.type == "PRIVATE" and sender_id == entry.creator_id:
                return entry
    return None


def get_all_group_entries(group_id: str) -> list[EntryCache]:
    result = []
    for entry in entries:
        if group_id in entry.enabled_groups or "0" in entry.enabled_groups:
            result.append(entry)
    return result


async def remove_group_entry(key: str, sender_id: str, group_id: str) -> Optional[int]:
    session = await get_session()
    async with session.begin():
        result = await session.execute(select(Entry).where(Entry.key == key or Entry.aliases.any(Alias.key == key)).where(Entry.enabled_groups.any(Group.group_id == group_id)))
        entry = result.scalar()
        if entry is None:
            return None
        await session.delete(entry)
        await session.commit()
        await fetch_all_entries()
        return 0


async def download_image(url: str, save_path: Path):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=qq_headers)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                logger.debug(f"Downloaded {url} and saved to {save_path}")
            else:
                logger.debug(f"Failed to download {url}. Status code: {response.status_code}")
        except Exception as e:
            logger.debug(f"Error while downloading {url}: {e}")


async def insert_new_entry(key: str, value: str, available: bool, called_times: int, creator_id: str,
                           creator_name: str, create_time, type: str, locked: bool, enabled_group: str) -> str:
    session = await get_session()
    async with session.begin():
        global entries
        add_entry = Entry(key=key, value=value, available=available, called_times=called_times, creator_id=creator_id,
                          creator_name=creator_name, create_time=create_time, type=type, locked=locked,
                          enabled_groups=[Group(group_id=enabled_group)], aliases=[])
        for entry in entries:
            if (entry.key == key or key in entry.aliases) and "0" in entry.enabled_groups:
                return "全局词条编辑失败哦~"
        is_exist = False
        for entry in entries:
            if (entry.key == key or key in entry.aliases) and enabled_group in entry.enabled_groups:
                is_exist = True
                break
        if is_exist:
            updated_entry = await session.execute(select(Entry).where(or_(Entry.key == key, Entry.aliases.any(Alias.key == key))).where(Entry.enabled_groups.any(Group.group_id == enabled_group)))
            updated_entry = updated_entry.scalar()
            updated_entry.value = value
            await session.commit()
            await fetch_all_entries()
            return "词条编辑成功啦~"
        # for entry in entries:
        #     if entry.key == key and enabled_group in entry.enabled_groups:
        #         add_entry.enabled_groups = [Group(group_id=group_id) for group_id in entry.enabled_groups]
        #         break
        session.add(add_entry)
        await session.commit()
        await fetch_all_entries()
        return "词条编辑成功啦~"


async def add_group_alias(key: str, alias: str, sender_id: str, group_id: str) -> Union[EntryCache, str]:
    for entry in entries:
        if entry.key == key and group_id in entry.enabled_groups:
            if alias in entry.aliases:
                return "这个别名已经存在啦~"
    session = await get_session()
    async with session.begin():
        result = await session.execute(select(Entry).
                                       filter(or_(Entry.key == key, Entry.aliases.any(Alias.key == key)))
                                       .where(Entry.enabled_groups
                                       .any(Group.group_id == group_id))
                                       .options(selectinload(Entry.enabled_groups))
                                       .options(selectinload(Entry.aliases))
                                       )
        entry = result.scalar()
        if entry is None:
            return "词条不存在哦~"
        entry.aliases.append(Alias(key=alias))
        new_entry = entry.to_cache()
        await session.commit()
        await fetch_all_entries()
        return new_entry
