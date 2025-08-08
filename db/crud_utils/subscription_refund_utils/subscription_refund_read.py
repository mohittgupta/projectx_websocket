import traceback

from config import logger
from db.database import db_session
from db.models.subscription_refund import subscription_refund


async def get_refunds_of_user(id):
    try:
        entity = db_session.query(subscription_refund).filter(subscription_refund.user_id == id).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []