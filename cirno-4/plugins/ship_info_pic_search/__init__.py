from nonebot import get_driver
from nonebot import get_driver, require, on_command, Bot, logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.plugin import PluginMetadata
from .config import Config
from .models import ShipGroup
from pathlib import Path


__plugin_meta__ = PluginMetadata(
    name="舰船信息库",
    description="查询舰船信息",
    usage=".舰船名",
    config=Config,
    extra={
        "is_local_plugin": True,
        "menus": [
            {
                "name": "舰船查询",
                "description": "查询厂商、系列、舰船数据",
                "functions": [
                    {
                        "name": ".舰船名",
                        "description": "获取舰船信息",
                    },
                    {
                        "name": ".厂商名",
                        "description": "获取该厂商的舰船列表",
                    },
                    {
                        "name": ".系列 + 系列名",
                        "description": "获取该系列的舰船列表",
                    },
                    {
                        "name": ".厂商表",
                        "description": "获取厂商列表",
                    },
                    {
                        "name": ".系列表",
                        "description": "获取数据库中的舰船系列列表",
                    }
                ]
            },
            {
                "name": "舰船查询编辑",
                "description": "修改现有舰船查询方式",
                "functions": [
                    {
                        "name": ".添加舰船别名 当前名字+#+要添加的别名",
                        "description": "为现有舰船添加别名, 添加后可使用别名触发舰船查询"
                    }
                ]
            }
        ]
    },
)


global_config = get_driver().config
config = Config.parse_obj(global_config)

ship_info_store_path = Path(config.ship_info_pic_path)

ship_group = ShipGroup()
ship_group.load_all()
manufacturer_names = ship_group.get_manufacturer_names()
series_names = ship_group.get_series_names()

send_ship_pic = on_command("", priority=5, block=True)
add_alias = on_command("添加舰船别名", aliases={"增加舰船别名"}, priority=5, block=True)
get_ships_by_manufacturer = on_command("", priority=5, block=True)
get_manufacturers = on_command("厂商", aliases={"厂商表", "厂商列表", "船厂", "船厂表"}, priority=5, block=True)
get_series = on_command("舰船系列表", aliases={"系列表", "系列列表"}, priority=5, block=True)
get_ships_by_series = on_command("系列", aliases={"舰船系列"}, priority=5, block=True)


@send_ship_pic.handle()
async def _send_ship_pic(arg: Message = CommandArg()):
    ship_name = str(arg).strip()
    ship = ship_group.get_ship_by_name(ship_name)
    if ship is None:
        send_ship_pic.block = False
        return
    ship_pic_path = ship_info_store_path / (ship.name + ".png")
    if ship_pic_path.exists():
        await send_ship_pic.finish(Message(MessageSegment.image(ship_pic_path)))
    else:
        await send_ship_pic.finish(f"找不到舰船: {ship.chinese_name}的信息图片哦~请确认提供给小九的文件夹位置是否正确哦~")


@add_alias.handle()
async def _add_alias(arg: Message = CommandArg()):
    if "#" not in str(arg):
        await add_alias.finish("请使用#分割舰船名和别名哦~")
    args = str(arg).strip().split("#")
    if len(args) != 2:
        await add_alias.finish("请提供舰船名和要添加的别名哦~")
    ship = ship_group.get_ship_by_name(args[0])
    if ship is None:
        await add_alias.finish(f"找不到舰船: {args[0]}哦~换个名字试试吧~")
        return
    alias = args[1]
    if alias in ship.alias:
        await add_alias.finish(f"舰船: {ship.chinese_name}已经有别名: {alias}了哦~")
    ship_group.add_alias(ship.local_name, alias)
    await add_alias.finish(f"已添加舰船: {ship.chinese_name}的别名: {alias}哦~\n当前别名有: {', '.join(list(set(ship.alias)))}")


@get_ships_by_manufacturer.handle()
async def _get_ships_manufacturer(arg: Message = CommandArg()):
    user_input = str(arg).strip()
    for manufacturer in manufacturer_names:
        if user_input in manufacturer:
            ships = ship_group.get_ships_by_manufacturer(user_input)
            text = f"厂商{user_input}的舰船有{len(ships)}艘哦~ \n"
            text += "\n".join([ship.chinese_name for ship in ships])
            text += "\n\n小伙伴可以使用.舰船名来查看舰船的信息哦~"
            await get_ships_by_manufacturer.finish(text)
    get_ships_by_manufacturer.block = False
    return


@get_manufacturers.handle()
async def _get_manufacturers():
    text = f"小九在数据库中找到了{len(manufacturer_names)}个厂商哦~\n小伙伴可以使用.厂商名来查看厂商的舰船哦~\n"
    text += "\n".join([f"{name}" for name, chinese_name in manufacturer_names])
    await get_manufacturers.finish(text)


@get_series.handle()
async def _get_series():
    text = f"小九找到了{len(series_names)}个舰船系列哦~\n小伙伴可以使用.系列+系列名 来查看舰船系列的舰船哦~\n"
    text += "\n".join(series_names)
    await get_series.finish(text)


@get_ships_by_series.handle()
async def _get_ships_by_series(arg: Message = CommandArg()):
    user_input = str(arg).strip()
    if user_input not in series_names:
        get_ships_by_series.block = False
        return
    ships = ship_group.get_ships_by_series(user_input)
    text = f"系列{user_input}的舰船有{len(ships)}艘哦~ \n"
    text += "\n".join([ship.chinese_name for ship in ships])
    text += "\n\n小伙伴可以使用.舰船名来查看舰船的信息哦~"
    await get_ships_by_series.finish(text)
