import traceback

from config import logger
from db.database import db_session



async def save_subscription_init(entity):
    try:
        db_session.add(entity)
        db_session.commit()
        db_session.close()
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
