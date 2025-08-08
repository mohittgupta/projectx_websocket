import traceback

from sqlalchemy import and_

from config import logger
from db.models.robinhood_access_token import robinhood_access_token
from db.database import db_session

async def get_robin_access_token_by_username(user_key):
    try:
        t = db_session.query(robinhood_access_token).filter(robinhood_access_token.user_random_id == user_key).first()
        db_session.close()
        return t
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None