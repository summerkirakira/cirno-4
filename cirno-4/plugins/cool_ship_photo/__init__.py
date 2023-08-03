from nonebot import get_driver, require, on_command

from .config import Config
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from pathlib import Path
import random


require("ship_info_pic_search")

from ..ship_info_pic_search import ship_group

global_config = get_driver().config
config = Config.parse_obj(global_config)
ship_pic_path = Path(config.ship_pic_path)


send_ship_photo = on_command("色图", aliases={"涩图", "船图"}, priority=5)


@send_ship_photo.handle()
async def _send_ship_photo(arg: Message = CommandArg()):
    ship_name = str(arg).strip()
    if ship_name == "":
        ship_image = random.choice(list(ship_pic_path.glob("*")))
    else:
        ship = ship_group.get_ship_by_name(ship_name)
        if ship is None:
            await send_ship_photo.finish(f"小九找不到舰船{ship_name}哦~")
        ship_image_name_list = []
        for image in ship.ship_pic:
            ship_image_name_list.append(image.url.split("/")[-1])
        ship_image = ship_pic_path / random.choice(ship_image_name_list)
    await send_ship_photo.finish(Message(MessageSegment.image(ship_image)))

