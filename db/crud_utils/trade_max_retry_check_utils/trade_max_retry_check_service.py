
import datetime
import traceback

from config import logger, max_check_per_minute_config
from db.crud_utils.trade_max_retry_check_utils.trade_max_retry_check_read import get_prev_row_mx_retry_check
from db.crud_utils.trade_max_retry_check_utils.trade_max_retry_check_write import save_max_retry_check
from db.models.trade_max_retry_check import trade_max_retry_check


async def check_max_retry_user(user_token,alert_json_data):
    try:
        is_websocket = True if 'by_socket' in alert_json_data else False
        logger.info(f"max trade check start for {user_token} is_websocket {is_websocket}")
        max_check_per_minute = max_check_per_minute_config
        if is_websocket:
            max_check_per_minute = max_check_per_minute_config + 10

        user_data = await get_prev_row_mx_retry_check(user_token)
        if user_data == None:
            logger.info(f"max trade first trade for {user_token}   is_websocket {is_websocket}")
            user_data = trade_max_retry_check()
            user_data.user_id = user_token
            user_data.max_trade = 1
            user_data.prev_date_time = datetime.datetime.now()
            await save_max_retry_check(user_data)
            return False
        else:
            if datetime.datetime.now().time().minute == user_data.prev_date_time.time().minute:
                max_retry = user_data.max_trade + 1
                if max_retry >= max_check_per_minute:
                    logger.info(f"max trade 5 trade found within minute for {user_token}   is_websocket {is_websocket}")
                    return True
                else:
                    user_data.max_trade = max_retry
                    await save_max_retry_check(user_data)
                    return False
            else:
                user_data.user_id = user_token
                user_data.max_trade = 1
                user_data.prev_date_time = datetime.datetime.now()
                await save_max_retry_check(user_data)
                return False

    except Exception as e:
        logger.error(f"error in checking max retry {traceback.format_exc()}")
        return False