from nonebot import get_driver, logger

from .config import Config

from sqlalchemy import create_engine, MetaData, Column, Integer, Table
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, sessionmaker


global_config = get_driver().config
config = Config.parse_obj(global_config)
driver = get_driver()

DATABASE_URL = f"mysql+aiomysql://{config.mysql_user}:{config.mysql_password}@{config.mysql_host}:{config.mysql_port}/{config.mysql_database}"
engine = create_async_engine(DATABASE_URL, echo=True)

Base = declarative_base()
metadata = MetaData()

async_connection = None


async def create_table_from_class(cls):
    table_name = cls.__tablename__
    columns = [col for col in cls.__dict__.values() if isinstance(col, Column)]
    table = Table(table_name, metadata, *columns)
    cls.__table__ = table

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


@driver.on_startup
async def main():
    async with engine.begin():
        logger.success(f"Connected to {config.mysql_host}")


async def get_session():
    return AsyncSession(engine)

