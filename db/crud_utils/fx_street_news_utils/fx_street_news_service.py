import datetime
import traceback

import pandas as pd

from config import logger
from db.crud_utils.fx_street_news_utils.fx_street_news_read import get_all_news_time_based


async def list_of_all_news(from_date,to_date):
    try:
        logger.info(f"getting all news {from_date} {to_date}")
        from_date =datetime.datetime.strptime(from_date,"%Y-%m-%d")
        to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d")
        news_map = await get_all_news_time_based(from_date,to_date)
        data = []
        for n in news_map:
            data.append({"title":n.title,"country":n.country,"date":n.date,"impact":n.impact,"forecast":n.forecast,"previous":n.previous,"url":n.url})
        return data
    except Exception as e:
        logger.error(f"error in saving root symbol {traceback.format_exc()}")
        return f"error {e}"