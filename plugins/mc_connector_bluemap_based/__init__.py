from nonebot import get_driver
from nonebot import on_command
from .config import Config
import httpx
from .models import Players

server_status = on_command("mc", aliases={"MC"}, priority=15, block=True)
plugin_config = Config.parse_obj(get_driver().config)


@server_status.handle()
async def _server_status():
    with httpx.Client() as client:
        r = client.get(f"http://{plugin_config.mc_server_url}/maps/overworld/live/players.json")
        players: Players = Players.parse_raw(r.text)

        server_text = plugin_config.mc_server_text.replace(r"\n", "\n")
        server_text = server_text.replace(r"{{player_num}}", str(len(players.players)))
        player_text = "\n".join([f"{player.name}({int(player.position.x)},{int(player.position.y)},{int(player.position.z)})" for player in players.players])
        server_text = server_text.replace(r"{{player_text}}", player_text)
        await server_status.finish(server_text)
