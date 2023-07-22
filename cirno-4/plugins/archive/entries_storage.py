from typing import Optional

from nonebot import require, logger, get_driver

from sqlalchemy.future import select

from sqlalchemy import update, delete, insert
from pathlib import Path

from sqlalchemy.orm import selectinload

require("database_connector")

import httpx

from ..database_connector import get_session
from .models import Entry, Group, EntryCache

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
        result = await session.execute(select(Entry).options(selectinload(Entry.enabled_groups)))
        global entries
        entries = [cache.to_cache() for cache in result.scalars().all()]
        return entries


@driver.on_startup
async def init_entries():
    await fetch_all_entries()


def get_entry(key: str, sender_id: str, group_id: str) -> Optional[EntryCache]:
    for entry in entries:
        if entry.key == key and ((group_id in entry.enabled_groups or "0" in entry.enabled_groups) or (entry.type == "PRIVATE" and sender_id == entry.creator_id)):
            return entry
    return None


async def remove_group_entry(key: str, sender_id: str, group_id: str) -> Optional[int]:
    session = await get_session()
    async with session.begin():
        result = await session.execute(select(Entry).where(Entry.key == key and group_id in Entry.enabled_groups))
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
                          enabled_groups=[Group(group_id=enabled_group)])
        for entry in entries:
            if entry.key == key and "0" in entry.enabled_groups:
                return "全局词条编辑失败哦~"
        is_exist = False
        for entry in entries:
            if entry.key == key and enabled_group in entry.enabled_groups:
                is_exist = True
                break
        if is_exist:
            await session.execute(update(Entry).where(Entry.key == key).where(Entry.enabled_groups.any(
                Group.group_id == enabled_group)).values(value=value))
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
