from datetime import datetime
from io import BytesIO

from nonebot import get_driver, require, on_command, Bot, logger
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.adapters import Message
from nonebot.plugin import PluginMetadata
import uuid
from .models import EntryCache

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="词条库",
    description="查询记录中的词条",
    usage=".词条",
    config=Config,
    extra={
        "is_local_plugin": True,
        "menus": [
            {
                "name": "词条查询",
                "description": "查询数据库",
                "functions": [
                    {
                        "name": ".词条",
                        "description": "获取存储的词条",
                    },
                    {
                        "name": ".查询词条",
                        "description": "获取已有词条的别名以及内容等信息",
                    }
                ]
            },
            {
                "name": "词条编辑",
                "description": "编辑或添加已有词条",
                "functions": [
                    {
                        "name": ".编辑词条 词条名+#+词条内容",
                        "description": "编辑已添加的词条，若词条不存在则添加词条, 词条仅在当前群生效, 词条内容可包含图片"
                    },
                    {
                        "name": ".查询词条 词条名",
                        "description": "获取已有词条的别名以及内容等信息"
                    },
                    {
                        "name": ".移除词条 词条名",
                        "description": "移除已添加的词条"
                    },
                    {
                        "name": ".添加别名 词条名+#+别名",
                        "description": "为已有词条添加别名, 添加后可使用别名触发词条"
                    }
                ]
            }
        ]
    },
)

require("database_connector")
require("nonebot_plugin_localstore")
require("nonebot_plugin_templates")
from ..templates_render.template_types import Func, Menu, Menus, Funcs
from ..templates_render.templates_render import menu_render

from .entries_storage import insert_new_entry, download_image, get_entry, remove_group_entry, add_group_alias, \
    get_all_group_entries, display_entry, fetch_all_entries, force_remove_group_entry, insert_global_new_entry
import nonebot_plugin_localstore as store

global_config = get_driver().config
config = Config.parse_obj(global_config)

driver = get_driver()

# @driver.on_startup
# async def create_table():
#     await create_table_from_class()

image_path = store.get_data_dir("archive") / "images"

logger.warning(image_path.absolute())

if not image_path.exists():
    image_path.mkdir(parents=True)

add_entries = on_command("编辑词条", aliases={"添加词条", "增加词条"}, priority=15, block=True)

send_entry = on_command("", priority=5, block=False)

remove_entry = on_command("移除词条", aliases={"删除词条"}, priority=15, block=True)

add_alias = on_command("添加别名", aliases={"增加别名"}, priority=15, block=True)

search_entry = on_command("搜索词条", aliases={"查找词条", "查询词条"}, priority=15, block=True)

all_entries = on_command("词条", aliases={"词条列表", "词条一览"}, priority=15, block=True)

refresh_archive = on_command("刷新词条", aliases={"同步词条", "更新词条"}, priority=15, block=True)

force_delete_entry = on_command("强制删除词条", aliases={"强制移除词条"}, priority=15, block=True, permission=SUPERUSER)

insert_global_entry = on_command("添加全局词条", aliases={"编辑全局词条"}, priority=15, block=True,
                                 permission=SUPERUSER)


async def modify_entry_text(arg: Message) -> str:
    modified_text = ""
    is_content = False
    for message in arg:
        if isinstance(message, MessageSegment):
            if message.is_text() and '#' in message.data['text']:
                modified_text += message.data['text'].split('#')[1] if len(message.data['text'].split('#')) == 2 else ""
                is_content = True
                continue
            if is_content:
                if message.is_text():
                    modified_text += message.data['text']
                elif message.type == "image":
                    image_url = message.data['url']
                    image_name = str(uuid.uuid4())
                    image_store_path = image_path / image_name
                    await download_image(image_url, image_store_path)
                    modified_text += f"[CQ:image,file=file:///{image_store_path.absolute()}]"
    return modified_text


@add_entries.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    arg_text = "".join([str(message_segment) for message_segment in arg])
    if "#" not in arg_text:
        await add_entries.finish("请使用#分割词条和内容")
    args = arg_text.split("#")
    if len(args) != 2:
        await add_entries.finish("请确保词条和内容之间只有一个#")
    if args[0] == "":
        await add_entries.finish("词条名不能为空")
    if args[1] == "":
        await add_entries.finish("词条内容不能为空")

    modified_text = modify_entry_text(arg)
    result = await insert_new_entry(
        key=args[0],
        value=await modified_text,
        available=True,
        called_times=0,
        creator_id=str(event.user_id),
        creator_name=event.sender.nickname,
        create_time=datetime.now(),
        type="REGULAR",
        locked=False,
        enabled_group=str(event.group_id)
    )
    await add_entries.finish(result)


@send_entry.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    arg_text = arg.extract_plain_text()
    if arg_text == "":
        await send_entry.finish("词条名不能为空哦~")
    entry = get_entry(key=arg_text, group_id=str(event.group_id), sender_id=str(event.user_id))
    if entry is not None:
        await bot.call_api('send_group_msg', message=entry.value, group_id=event.group_id)
        return
    send_entry.block = False


@remove_entry.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    arg_text = arg.extract_plain_text()
    if arg_text == "":
        await remove_entry.finish("词条名不能为空哦~")
    entry = await remove_group_entry(key=arg_text, group_id=str(event.group_id), sender_id=str(event.user_id))
    if entry is not None:
        await remove_entry.finish("词条删除成功哦~")
    else:
        await remove_entry.finish("词条不存在哦~")


@add_alias.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    arg_text = arg.extract_plain_text()
    if arg_text == "":
        await add_alias.finish("别名不能为空哦~请使用.添加别名 [词条名]#[别名]来为词条添加一个别名~")
    args = arg_text.split("#")
    if len(args) != 2:
        await add_alias.finish("请使用.添加别名 [词条名]#[别名]来为词条添加一个别名~")
    result = await add_group_alias(key=args[0], alias=args[1], group_id=str(event.group_id),
                                   sender_id=str(event.user_id))
    if isinstance(result, EntryCache):
        await add_alias.finish(f"别名添加成功哦~当前词条[{result.key}]的别名有[{', '.join(result.aliases)}]。")
    else:
        await add_alias.finish(f"别名添加失败QAQ{result}")


@search_entry.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg(), bot: Bot = None):
    arg_text = arg.extract_plain_text()
    if arg_text == "":
        await search_entry.finish("词条名不能为空哦~")
    entry = get_entry(key=arg_text, group_id=str(event.group_id), sender_id=str(event.user_id))
    if entry is not None:
        entry_info = f"以下为词条信息~\n词条名：[{entry.key}]\n"
        if len(entry.aliases) > 0:
            entry_info += f"别名: [{', '.join(entry.aliases)}]\n"
        entry_info += f"创建者：{entry.creator_name}\n"
        entry_info += f"创建时间：{entry.create_time}\n"
        entry_info += f"内容为：\n{entry.value}"
        try:
            await bot.call_api('send_group_msg', message=entry_info, group_id=event.group_id)
        except Exception as e:
            logger.error(f"发送词条信息失败：{e}")
            await search_entry.finish("词条信息发送失败QAQ可能原因是图片已过期~请更新词条图片后重试~")
        return
    else:
        await search_entry.finish("词条不存在哦~")


@all_entries.handle()
async def _(event: GroupMessageEvent, bot: Bot = None):
    entries = get_all_group_entries(group_id=str(event.group_id))
    if len(entries) == 0:
        await all_entries.finish("当前群没有词条哦~")
    funcs = []

    if len(entries) < 100:
        column_num = 2
    else:
        column_num = len(entries) // 50

    for entry in entries:
        funcs.append(
            Func(
                name=entry.key,
                desc=display_entry(entry.value),
            )
        )
    menu = Menu("词条列表", des="使用.词条名来获取词条", funcs=funcs)
    pic_bytes = await menu_render(Menus(menu), 400 * column_num)
    await all_entries.finish(message=Message(MessageSegment.image(pic_bytes)))


@refresh_archive.handle()
async def _():
    try:
        entries = await fetch_all_entries()
    except Exception as e:
        logger.error(f"刷新词条缓存失败：{e}")
        await refresh_archive.finish("刷新失败QAQ")
    await refresh_archive.finish(f"词条库与数据库同步成功哦~当前词条数量为{len(entries)}~")


@force_delete_entry.handle()
async def _(arg: Message = CommandArg()):
    arg_text = arg.extract_plain_text()
    if arg_text == "":
        await force_delete_entry.finish("词条名不能为空哦~")
    entry = await force_remove_group_entry(key=arg_text)
    if entry is not None:
        await force_delete_entry.finish("词条删除成功哦~")
    else:
        await force_delete_entry.finish("词条不存在哦~")


@insert_global_entry.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    arg_text = arg.extract_plain_text()
    if arg_text == "":
        await insert_global_entry.finish("词条名不能为空哦~")
    await insert_global_new_entry(key=arg_text.split("#")[0], value=await modify_entry_text(arg), creator_id=str(event.user_id),
                                          creator_name=event.sender.nickname, create_time=datetime.now(), locked=False)
    await insert_global_entry.finish("词条添加成功哦~")
