import traceback

from db.database import db_session
from config import logger


async def save_sub_accounts(data):
    try:
        db_session.add(data)
        db_session.commit()
        db_session.close()
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()