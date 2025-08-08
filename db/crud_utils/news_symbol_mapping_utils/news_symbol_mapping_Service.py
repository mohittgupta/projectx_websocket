import traceback

import pandas as pd

from config import logger
from db.crud_utils.news_symbol_mapping_utils.news_symbol_mapping_read import get_by_tradovate_symbol_mapping, \
    getting_all_news_symbol_map
from db.crud_utils.news_symbol_mapping_utils.news_symbol_mapping_write import save_news_symbol_map, del_news_symbol_map
from db.models.news_symbol_mapping import news_symbol_mapping


async def saving_news_symbol_mapping(user,tradovate_root_symbol,country):
    try:
        logger.info(f"saving news map symbol tradovate_root_symbol {tradovate_root_symbol}  country {country}")
        news_map = await get_by_tradovate_symbol_mapping(tradovate_root_symbol)
        if news_map == None:
            news_map = news_symbol_mapping()
        news_map.tradovate_root_symbol = tradovate_root_symbol
        news_map.country = country
        await save_news_symbol_map(news_map)
        return "Successfully saved"
    except Exception as e:
        logger.error(f"error in saving root symbol {traceback.format_exc()}")
        return f"error {e}"
async def getting_news_symbol_mapping(user):
    try:
        news_map = await getting_all_news_symbol_map()
        data = []
        for n in news_map:
            data.append({"tradovate_root_symbol":n.tradovate_root_symbol,"country":n.country})
        return data
    except Exception as e:
        logger.error(f"error in getting root symbol {traceback.format_exc()}")
        return f"error {e}"

async def deleting_news_symbol_mapping(user,tradovate_root_symbol):
    try:
        news_map = await get_by_tradovate_symbol_mapping(tradovate_root_symbol)
        if news_map != None:
            await del_news_symbol_map(news_map)
        return f"Successfully Delete"
    except Exception as e:
        logger.error(f"error in getting root symbol {traceback.format_exc()}")
        return f"error {e}"
