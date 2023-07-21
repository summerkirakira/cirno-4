from nonebot import get_driver, require, on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters import Message
from typing import Annotated

from .config import Config

from .models import Archive

require("database_connector")

from ..database_connector import create_table_from_class
from .entries_storage import insert_new_entry

global_config = get_driver().config
config = Config.parse_obj(global_config)


driver = get_driver()


# @driver.on_startup
# async def create_table():
#     await create_table_from_class()


add_entries = on_command("编辑词条", aliases={"添加词条", "增加词条"}, priority=15, block=True)


@add_entries.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    arg = arg.extract_plain_text()
    if "#" not in arg:
        add_entries.finish("请使用#分割词条和内容")
    args = arg.split("#")
    if len(args) != 2:
        add_entries.finish("请确保词条和内容之间只有一个#")
    if args[0] == "":
        add_entries.finish("词条名不能为空")
    if args[1] == "":
        add_entries.finish("词条内容不能为空")

    await insert_new_entry(
        creator_id=event.user_id,
        content=args[1],
        keywords=args[0],
        enabled_groups=str(event.group_id),
        creator=str(event.sender.nickname)
    )