from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    mc_server_url: str
    mc_server_text: str
