from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):

    ship_info_pic_path: str
