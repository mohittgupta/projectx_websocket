import traceback

from config import logger
from db.models.server_start_time import server_start_time
from db.database import db_session


async def get_first_row():
    try:
        entity = db_session.query(server_start_time).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None