from typing import Optional

import loguru
from nonebot import get_driver, require, get_bots
from nonebot import on_command, logger
from .config import Config
import httpx
from .models import Players

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

server_status = on_command("mc", aliases={"MC"}, priority=15, block=True)
plugin_config = Config.parse_obj(get_driver().config)

driver = get_driver()

players: Optional[Players] = Players(players=[])


async def get_players():
    with httpx.Client() as client:
        r = client.get(f"http://{plugin_config.mc_server_url}/maps/overworld/live/players.json")
        global players
        players = Players.parse_raw(r.text)


@server_status.handle()
async def _server_status():
    with httpx.Client() as client:
        await get_players()
        global players
        server_text = plugin_config.mc_server_text.replace(r"\n", "\n")
        server_text = server_text.replace(r"{{player_num}}", str(len(players.players)))
        player_text = "\n".join([f"{player.name}({int(player.position.x)},{int(player.position.y)},{int(player.position.z)})" for player in players.players])
        server_text = server_text.replace(r"{{player_text}}", player_text)
        await server_status.finish(server_text)


@driver.on_startup
async def _():
    await get_players()


@scheduler.scheduled_job("interval",
                         seconds=plugin_config.mc_server_update_interval)
async def _():
    try:
        new_players_list = []
        with httpx.Client() as client:
            r = client.get(f"http://{plugin_config.mc_server_url}/maps/overworld/live/players.json")
            new_players: Players = Players.parse_raw(r.text)
        global players
        for new_player in new_players.players:
            is_exist = False
            for old_player in players.players:
                if new_player.name == old_player.name:
                    is_exist = True
                    break
            if not is_exist:
                new_players_list.append(new_player)
        players = new_players
        if len(new_players_list) > 0:
            for broadcast_group in plugin_config.broadcast_group:
                for bot_id in get_bots():
                    if bot_id == str(broadcast_group.bot_id):
                        await get_bots()[bot_id].send_group_msg(group_id=broadcast_group.group_id, message=f"小伙伴{','.join([player.name for player in new_players_list])}上线啦！")
    except httpx.ReadTimeout as e:
        logger.warning(f"Refresh players list timeout")
    except Exception as e:
        logger.error(f"Refresh players list failed: {e}")





