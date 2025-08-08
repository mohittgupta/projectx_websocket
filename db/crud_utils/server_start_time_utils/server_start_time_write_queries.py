import traceback

from db.models.server_start_time import server_start_time
from db.crud_utils.server_start_time_utils.server_start_time_read_queries import *
from db.database import db_session
from config import logger,default_setting
import datetime
async def set_current_time():
    try:
        start_time = datetime.datetime.now()
        if default_setting.get("timezone") == "UTC":
            start_time = datetime.datetime.utcnow()
        else:
            start_time = datetime.datetime.now()
        logger.info(f"saving server start datetime {start_time}")
        server_time = await get_first_row()
        if server_time is not None:
            server_time.start_time = start_time
        else:
            server_time = server_start_time(row_id=1, start_time=start_time)
        try:
            db_session.add(server_time)
            db_session.commit()
            db_session.close()
        except Exception as e:
            logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
            db_session.rollback()
            db_session.close()
    except Exception as e:
        logger.error(f"error in setting start time {traceback.format_exc()}")