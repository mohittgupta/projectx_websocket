import traceback

from config import logger
from db.database import db_session

async def save_manual_pause_data(e):
    current_id = 0
    try:
        db_session.add(e)
        db_session.commit()
        current_id =e.row_id
        db_session.close()
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
    return current_id
async def del_manual_pause_data(e):
    try:
        db_session.delete(e)
        db_session.commit()
        db_session.close()
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()