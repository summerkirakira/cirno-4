from datetime import datetime
from nonebot import get_driver, require, on_command, Bot
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.adapters import Message
import uuid

from .config import Config


require("database_connector")
require("nonebot_plugin_localstore")

from .entries_storage import insert_new_entry, download_image, get_entry, remove_group_entry
import nonebot_plugin_localstore as store

global_config = get_driver().config
config = Config.parse_obj(global_config)


driver = get_driver()


# @driver.on_startup
# async def create_table():
#     await create_table_from_class()

image_path = store.get_data_dir("archive") / "images"
if not image_path.exists():
    image_path.mkdir(parents=True)


add_entries = on_command("编辑词条", aliases={"添加词条", "增加词条"}, priority=15, block=True)

send_entry = on_command("", priority=5, block=False)

remove_entry = on_command("删除词条", aliases={"删除词条", "移除词条"}, priority=15, block=True)


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
    await insert_new_entry(
        key=args[0],
        value=modified_text,
        available=True,
        called_times=0,
        creator_id=str(event.user_id),
        creator_name=event.sender.nickname,
        create_time=datetime.now(),
        type="REGULAR",
        locked=False,
        enabled_group=str(event.group_id)
    )
    await add_entries.finish("词条添加成功哦~")


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