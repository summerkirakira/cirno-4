from nonebot import get_driver, logger

from .config import Config

from sqlalchemy import create_engine, MetaData, Column, Integer, Table
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
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
    async with engine.begin() as conn:
        # 创建表格（如果尚不存在）
        await conn.run_sync(Base.metadata.create_all)


@driver.on_startup
async def main():
    async with engine.begin():
        logger.success(f"Connected to {config.mysql_host}")


async def get_session():
    return AsyncSession(engine)

