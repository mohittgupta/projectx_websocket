import datetime
import traceback

from config import logger
from db.crud_utils.watch_client_order_id_map_utils.watch_client_order_id_map_write import write_watch_order_map
from db.models.watch_client_order_id_map import watch_client_order_id_map


async def save_watch_map_order_id(master_token,user_token,master_id,client_id,master_account_id=None,child_account_id="",msg=""):
    try:
        wco = watch_client_order_id_map()
        wco.master_token = master_token
        wco.child_token = user_token
        wco.master_order_id = master_id
        wco.child_order_id = client_id
        wco.order_type = ""
        wco.datetime = datetime.datetime.now()

        wco.master_account_id = master_account_id
        wco.child_account_id = child_account_id
        wco.msg = msg
        await write_watch_order_map(wco)
    except Exception as e:
        logger.error(f"error in watch map saving {traceback.format_exc()}")