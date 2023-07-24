import contextlib
from typing import Any, Dict

from nonebot import on_endswith, on_fullmatch, on_regex
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import Endswith, RegexDict
from nonebot.plugin import PluginMetadata
from .exchangerate import exchange_currency, get_currency_info, get_currency_list

from .config import Config

exchange = on_regex(r"^\.(?P<amount>\d+\.?\d*)(?P<currency>[\u4e00-\u9fff]{1,5}$)")
__plugin_meta__ = PluginMetadata(
    name="汇率查询",
    description="查询当前各货币的汇率",
    usage=".词条",
    config=Config,
    extra={
        "is_local_plugin": True,
        "menus": [
            {
                "name": "汇率查询",
                "description": "查询当前各货币的汇率",
                "functions": [
                    {
                        "name": ".数量+货币名",
                        "description": "查询该货币的汇率",
                    }
                ]
            }
        ]
    },
)


@exchange.handle()
async def _(matched: Dict[str, Any] = RegexDict()) -> None:
    with contextlib.suppress(ValueError):
        total = exchange_currency(matched["currency"], float(matched["amount"]))
        from .exchangerate import update_time
        msg = f"约合{total}人民币哦~\n当前汇率：1{matched['currency']}={round(total/float(matched['amount']), 2)}人民币\n更新时间：{update_time}"
        await exchange.send(msg, reply_message=True)


# info = on_endswith("汇率")


# @info.handle()
# async def _(event: MessageEvent, suffix: str = Endswith()) -> None:
#     txt = event.get_plaintext()
#     try:
#         currency = txt[: -len(suffix)]
#         if len(currency) > 5:
#             return
#         msg = get_currency_info(currency)
#     except ValueError as e:
#         msg: str = str(e)
#     await info.send(msg)


# statement = on_fullmatch(("货币列表", "汇率列表"))


# @statement.handle()
# async def _() -> None:
#     currency_list = get_currency_list()
#     msg = "支持查询的货币:\n" + "\n".join(currency_list)
#     await statement.send(msg)