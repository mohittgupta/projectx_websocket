import traceback

from config import logger
from db.models.payment_init import payment_init
from db.database import db_session
import re

async def get_by_payment_order_id(order_id):
    try:
        entity = db_session.query(payment_init).filter(payment_init.order_id == order_id).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None