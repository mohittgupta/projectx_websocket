import re
import traceback

import pandas as pd

from config import logger
from db.crud_utils.manual_trade_pause_accounts_utils.manual_trade_pause_accounts_read import \
    get_accounts_by_user_id_trade_pause_timing
from db.crud_utils.manual_trade_pause_accounts_utils.manual_trade_pause_accounts_write import del_manual_pause_accounts, \
    save_manual_pause_accounts
from db.crud_utils.manual_trade_pause_utils.manual_trade_pause_read import get_by_user_id_manual_trade_pause, \
    get_all_by_user_id_manual_trade_pause, get_all_by_id_user_id_manual_trade_pause
from db.crud_utils.manual_trade_pause_utils.manual_trade_pause_write import save_manual_pause_data, \
    del_manual_pause_data
from db.crud_utils.news_trade_pause_utils.news_trade_pause_read import get_by_user_id_news_pause_data, \
    getting_all_news_pause_data
from db.crud_utils.news_trade_pause_utils.news_trade_pause_write import save_news_pause_trade_data, \
    del_news_pause_trade_data
from db.models.manual_trade_pause import manual_trade_pause
from db.models.manual_trade_pause_accounts import manual_trade_pause_accounts
from db.models.news_trade_pause import news_trade_pause


async def get_user_paused_time(user):
    try:
        user_pause_data = await get_all_by_user_id_manual_trade_pause(user.random_id)
        if user_pause_data == None or len(user_pause_data) == 0:
            return []
        else:
            res = []
            for upd in user_pause_data:
                accs = []
                connection_names = []
                dbaccounts = await get_accounts_by_user_id_trade_pause_timing(user.id, upd.row_id)
                if dbaccounts != None and len(dbaccounts) > 0:
                    for ac in dbaccounts:
                        broker = re.sub(r'\d+', '', ac.connection_name)
                        accs.append({"account_name":ac.acc_name, "connection_name":ac.connection_name, "broker":broker})


                res.append({"id": upd.row_id,"start": upd.start_stop_time, "stop": upd.end_stop_time, "closed_all": upd.closed_all,"accounts":accs})

            return res

    except Exception as e:
        logger.error(f"error insaving user news paused time {traceback.format_exc()}")
        return f"Error {e}"


async def save_user_paused_time(user,id, start_after_in_minute, stop_before_in_minute,closed_all=False,accounts=[]):
    try:
        user_pause_data = None
        if id != 0:
            logger.info(f"updating old pause time and {id} {user.random_id}")
            user_pause_data = await get_all_by_id_user_id_manual_trade_pause(user.random_id,id)
        current_id = 0
        if user_pause_data == None:
            user_pause_data = manual_trade_pause()
        user_pause_data.user_id = user.random_id
        user_pause_data.start_stop_time = start_after_in_minute
        user_pause_data.end_stop_time = stop_before_in_minute
        user_pause_data.closed_all = closed_all
        current_id = await save_manual_pause_data(user_pause_data)

        dbaccounts = await get_accounts_by_user_id_trade_pause_timing(user.id,id)
        if dbaccounts != None and len(dbaccounts) > 0:
            for ac in dbaccounts:
                await del_manual_pause_accounts(ac)
        if not closed_all:
            for ac in accounts:
                account_name = ac['account_name']
                connection_name = ac['connection_name']
                accounts_d = manual_trade_pause_accounts()
                accounts_d.user_id = user.id
                accounts_d.timming_row_id = current_id
                accounts_d.acc_name = account_name
                accounts_d.connection_name = connection_name
                await save_manual_pause_accounts(accounts_d)
        # user_pause_data = await get_all_by_user_id_manual_trade_pause(user.random_id)
        # if start_after_in_minute == "" or stop_before_in_minute == "":
        #     if user_pause_data != None:
        #         await del_manual_pause_data(user_pause_data)
        #     return "Successfully Delete"
        # else:

        return "Successfully Saved"
    except Exception as e:
        logger.error(f"error insaving user news paused time {traceback.format_exc()}")
        return f"Error {e}"



async def del_user_paused_time(user,id):
    try:
        logger.info(f"deleting old pause time and {id} {user.random_id}")
        user_pause_data = await get_all_by_id_user_id_manual_trade_pause(user.random_id, id)
        if user_pause_data != None:
            await del_manual_pause_data(user_pause_data)
        return "Successfully Delete"
    except Exception as e:
        logger.error(f"error insaving user news paused time {traceback.format_exc()}")
        return f"Error {e}"

async def save_user_news_paused_time(user, stop_before_in_minute, start_after_in_minute, closed_position_open_order):
    try:
        user_pause_data = await get_by_user_id_news_pause_data(user.random_id)
        if user_pause_data == None:
            user_pause_data = news_trade_pause()
        user_pause_data.user_id = user.random_id
        user_pause_data.start_after_in_minute = int(start_after_in_minute)
        user_pause_data.stop_before_in_minute = int(stop_before_in_minute)
        user_pause_data.closed_position_open_order = closed_position_open_order
        await save_news_pause_trade_data(user_pause_data)
        return "Successfully Saved"
    except Exception as e:
        logger.error(f"error insaving user news paused time {traceback.format_exc()}")
        return f"Error {e}"


async def getting_user_news_paused_time(user):
    try:
        user_pause_data = await getting_all_news_pause_data(user.random_id)
        data = []
        for n in user_pause_data:
            data.append(
                {"stop_before_in_minute": n.stop_before_in_minute, "start_after_in_minute": n.start_after_in_minute,
                 "closed_position_open_order": n.closed_position_open_order})
        return data
    except Exception as e:
        logger.error(f"error insaving user news paused time {traceback.format_exc()}")
        return []


async def deleting_user_news_paused_time(user):
    try:
        user_pause_data = await get_by_user_id_news_pause_data(user.random_id)
        if user_pause_data != None:
            await del_news_pause_trade_data(user_pause_data)
        return f"Successfully Delete"
    except Exception as e:
        logger.error(f"error in getting root symbol {traceback.format_exc()}")
        return f"error {e}"
