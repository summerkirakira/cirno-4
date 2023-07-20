from datetime import datetime
from typing import Dict, List, Tuple, Optional

import httpx
from nonebot import require
from nonebot.log import logger
from pydantic import BaseModel

from .config import config

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

import json
import pathlib


trans_dict = {
    "人民币": "CNY",
    "美元": "USD",
    "美金": "USD",
    "美刀": "USD",
    "韩国元": "KRW",
    "韩元": "KRW",
    "新台币": "TWD",
    "日元": "JPY",
    "澳大利亚元": "AUD",
    "澳币": "AUD",
    "英镑": "GBP",
    "印尼卢比": "IDR",
    "新西兰元": "NZD",
    "新加坡元": "SGD",
    "泰铢": "THB",
    "瑞典克朗": "SEK",
    "瑞士法郎": "CHF",
    "卢布": "RUB",
    "菲律宾比索": "PHP",
    "港币": "HKD",
    "林吉特": "MYR",
    "欧元": "EUR",
    "印度卢比": "INR",
    "卢比": "INR",
    "丹麦克朗": "DKK",
    "加拿大元": "CAD",
    "挪威克朗": "NOK",
    "阿联酋迪拉姆": "AED",
    "沙特里亚尔": "SAR",
    "巴西里亚尔": "BRL",
    "澳门元": "MOP",
    "澳元": "MOP",
    "南非兰特": "ZAR",
    "土耳其里拉": "TRY",
}


class ExchangeRate(BaseModel):
    name: str
    """货币名称"""
    unit: int = 1
    """交易单位"""
    spot_exchange: float = 0
    """现汇买入价"""
    cash_purchase: float = 0
    """现钞买入价"""
    cash_sellout: float
    """现钞卖出价"""
    conversion: float = 0
    """中行折算价"""

    def exchange(self, amount: float) -> float:
        """CNY兑换外币"""
        sums = self.cash_sellout / self.unit * amount
        if config.exchange_decimals:
            return round(sums, config.exchange_decimals)
        return round(sums)


exchange_dict: Dict[str, ExchangeRate] = {}

external_currency_list: List[Dict[str, str]] = json.load(
    (pathlib.Path(__file__).parent / "currency_list.json").open("r", encoding="utf-8")
)

for item in external_currency_list:
    trans_dict[item["name"]] = item["code"]

update_time = ""


@scheduler.scheduled_job(
    "interval",
    minutes=30,
    args=[config.exchange_app_key],
    next_run_time=datetime.now(),
    misfire_grace_time=30,
)
async def fetch_exchange(app_key: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://v6.exchangerate-api.com/v6/{app_key}/latest/CNY"
        )
    result = response.json()
    conversion_rates_dict = response.json()["conversion_rates"]
    global exchange_list
    exchange_dict.clear()
    for k, v in conversion_rates_dict.items():
        currency_chinese_names = get_currency_chinese_names(k)
        for chinese_name in currency_chinese_names:
            exchange_dict[chinese_name] = ExchangeRate(name=chinese_name, cash_sellout=1 / v)
        # if len(currency_chinese_names) == 0:
        #     logger.warning(f"未知货币: {k}")
    global update_time
    update_time = datetime.fromtimestamp(result["time_last_update_unix"])
    logger.debug(f"汇率更新成功! 更新时间: {update_time}")


def get_exchangerate(name: str) -> ExchangeRate:
    try:
        return exchange_dict[name]
    except KeyError:
        raise ValueError("查找的货币不存在")


def exchange_currency(name: str, amount: float) -> float:
    er = get_exchangerate(name)
    return er.exchange(amount)


def get_currency_info(name: str) -> str:
    er = get_exchangerate(name)
    return (
        f"货币名称: {er.name}\n"
        f"现汇买入价: {er.spot_exchange}\n"
        f"现钞买入价: {er.cash_purchase}\n"
        f"现钞卖出价: {er.cash_sellout}\n"
        f"中行折算价: {er.conversion}\n"
        f"更新时间: {update_time}"
    )


def get_currency_list() -> List[str]:
    return list(exchange_dict.keys())


def get_currency_chinese_names(name: str) -> List[str]:
    chinese_name_list = []
    for k, v in trans_dict.items():
        if name == v:
            chinese_name_list.append(k)
    return chinese_name_list
