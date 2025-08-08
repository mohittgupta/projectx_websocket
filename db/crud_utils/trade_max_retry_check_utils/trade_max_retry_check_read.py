import traceback

from sqlalchemy import or_

from config import logger
from db.models.trade_max_retry_check import trade_max_retry_check
from db.database import db_session


async def get_prev_row_mx_retry_check(user_token):
    try:
        entity = db_session.query(trade_max_retry_check).filter(trade_max_retry_check.user_id == user_token).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None