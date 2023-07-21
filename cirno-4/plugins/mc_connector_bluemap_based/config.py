from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    class BroadcastGroup(BaseModel):
        bot_id: int
        group_id: int

    mc_server_url: str
    mc_server_text: str
    broadcast_group: list[BroadcastGroup] = []
    mc_server_update_interval: int = 20
