import traceback

from config import logger
from db.database import db_session
from db.models.rollover_instrument_history import rollover_instrument_history


async def get_all_rollover_hist():
    try:
        entity = db_session.query(rollover_instrument_history).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []