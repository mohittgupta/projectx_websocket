import traceback

from sqlalchemy import and_

from config import logger
from db.models.discount import discount
from db.database import db_session

async def get_by_code_discount_order(code):
    try:
        entity = db_session.query(discount).filter(discount.code == code).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_by_code_discount_order_active(code):
    try:
        entity = db_session.query(discount).filter(discount.code == code).filter(discount.active == True).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_all_discount_order():
    try:
        entity = db_session.query(discount).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []