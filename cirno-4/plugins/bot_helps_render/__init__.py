from pathlib import Path
from typing import List

import nonebot
from nonebot import get_driver, on_command, require
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import Plugin
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.params import CommandArg

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

require("nonebot_plugin_templates")
from ..templates_render.template_types import Func, Menu, Menus, Funcs
from ..templates_render.templates_render import menu_render, colorlist_render

plugin_names: set[str] = nonebot.get_available_plugin_names()

driver = get_driver()
plugin_help_info_dict = {}


@ driver.on_startup
async def load_plugins():
    for plugin_name in plugin_names:
        plugin: Plugin = nonebot.get_plugin(plugin_name)
        if plugin.metadata is None:
            continue
        if "is_local_plugin" in plugin.metadata.extra and plugin.metadata.extra["is_local_plugin"]:
            plugin_help_info_dict[plugin.metadata.name] = {
                "name": plugin.metadata.name,
                "description": plugin.metadata.description,
                "menus": plugin.metadata.extra["menus"]
            }


help_render = on_command("帮助", aliases={"help"}, priority=15, block=True)


@help_render.handle()
async def _help_render(event: GroupMessageEvent, arg: Message = CommandArg()):
    arg_text = arg.extract_plain_text()
    if not arg_text:
        funcs = []
        for plugin_name in plugin_help_info_dict:
            funcs.append(Func(
                name=plugin_help_info_dict[plugin_name]["name"],
                desc=plugin_help_info_dict[plugin_name]["description"]
            ))
        funcs.append(Func(
            name=".帮助 + 功能名",
            desc="获取详细小九功能使用帮助"
        ))
        menu = Menu("使用帮助", des="获取小九功能使用帮助", funcs=Funcs(funcs))
        pic_bytes = await menu_render(Menus(menu), 800)
        await help_render.finish(message=Message(MessageSegment.image(pic_bytes)))
    else:
        if arg_text not in plugin_help_info_dict:
            await help_render.finish("小九做不到呢~请使用.帮助+功能名获取详细帮助~")
        menus = []
        for menu in plugin_help_info_dict[arg_text]["menus"]:
            funcs = []
            for func in menu["functions"]:
                funcs.append(Func(
                    name=func["name"],
                    desc=func["description"]
                ))
            menus.append(Menu(
                name=menu["name"],
                des=menu["description"],
                funcs=Funcs(funcs)
            ))
        pic_bytes = await menu_render(Menus(menus), 800)
        await help_render.finish(message=Message(MessageSegment.image(pic_bytes)))

