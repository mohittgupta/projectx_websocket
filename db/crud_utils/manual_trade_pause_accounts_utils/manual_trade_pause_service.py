import datetime
import traceback

import pytz

from business_logic.object_factory import convert_current_time_in_est
from business_logic.tradovate_connector import closing_open_order_execute
from config import logger
from db.crud_utils.login_central_utils.login_central_read_queries import get_by_user_id
from db.crud_utils.manual_trade_pause_accounts_utils.manual_trade_pause_accounts_read import \
    get_trade_pause_timing_for_closing, get_accounts_by_user_id_trade_pause_timing


async def manual_trade_pause_closing_check():
    try:
        pause_Data = await get_trade_pause_timing_for_closing()
        for manual_pause in pause_Data:
            user= await get_by_user_id(manual_pause.user_id)
            accounts = await get_accounts_by_user_id_trade_pause_timing(user.id, manual_pause.row_id)
            if accounts != None and len(accounts) > 0:
                all_accounts = []
                for ac in accounts:
                    all_accounts.append(ac.acc_name)

            start_time, end_time = None, None
            start_time = datetime.datetime.strptime(
                str(datetime.datetime.now().date()) + " " + manual_pause.start_stop_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(
                str(datetime.datetime.now().date()) + " " + manual_pause.end_stop_time, "%Y-%m-%d %H:%M:%S")
            second_start_time, second_end_time, prev_start_time = None, None, None

            if start_time > end_time:
                logger.info(
                    f"{user.random_id} end time is low then start time so adding one day in end time {end_time}  start_time {start_time} ")
                end_time = datetime.datetime.strptime(
                    str((datetime.datetime.now() + datetime.timedelta(
                        days=1)).date()) + " " + manual_pause.end_stop_time, "%Y-%m-%d %H:%M:%S")
                prev_start_time = datetime.datetime.strptime(
                    str((datetime.datetime.now() - datetime.timedelta(
                        days=1)).date()) + " " + manual_pause.start_stop_time, "%Y-%m-%d %H:%M:%S")
                second_start_time = datetime.datetime.strptime(
                    str((datetime.datetime.now()).date()) + " 00:00:01", "%Y-%m-%d %H:%M:%S")
                second_end_time = datetime.datetime.strptime(
                    str((datetime.datetime.now()).date()) + " " + manual_pause.end_stop_time, "%Y-%m-%d %H:%M:%S")

            current_est_time = convert_current_time_in_est()
            logger.info(
                f"cehcing mauanl pause time Start time {start_time} End time {end_time} current time {current_est_time}  second_start_time {second_start_time}  second_end_time {second_end_time}  prev_start_time {prev_start_time}")
            ny_tz = pytz.timezone("America/New_York")
            start_time = ny_tz.localize(start_time)
            end_time = ny_tz.localize(end_time)
            if second_start_time != None:
                second_start_time = ny_tz.localize(second_start_time)
                second_end_time = ny_tz.localize(second_end_time)
            if prev_start_time != None:
                prev_start_time = ny_tz.localize(prev_start_time)
            logger.info(
                f"after  convert cehcing mauanl pause time Start time {start_time} End time {end_time} current time {current_est_time} second_start_time {second_start_time} second_end_time {second_end_time}")
            if (current_est_time > end_time):
                logger.info(
                    f"1 closing  orders {current_est_time} start_time {start_time} current_est_time {current_est_time} end_time {end_time}")
                for ac in accounts:
                    await closing_open_order_execute(user, 0, 0, 0, "", tradovate_account_id=ac.id,
                                               tradovate_account_name=ac)
    except Exception as e:
        logger.error(f"error in closing user_orders,position {traceback.format_exc()}")