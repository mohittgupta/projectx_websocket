import traceback
from typing import Optional

from sqlalchemy import and_

from config import logger
from db.models.payment_history import payment_history
from db.database import db_session

async def get_all_user_payment_hist_list():
    try:
        entity = db_session.query(payment_history).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []
async def get_all_user_payment_hist_list_by_code(referral_code):
    try:
        entity = db_session.query(payment_history).filter(payment_history.other_user_referral_code == referral_code).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []
async def get_all_user_payment_hist_list_sepecific_user(id):
    try:
        entity = db_session.query(payment_history).filter(payment_history.user_id == id).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_current_payment_history(user_id: int) -> Optional[payment_history]:
    try:
        entity = (
            db_session.query(payment_history)
            .filter(payment_history.user_id == user_id)
            .order_by(payment_history.created.desc())
            .first()
        )
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None


async def get_all_payment_history(user_id: int) -> list[payment_history]:
    try:
        entity = (
            db_session.query(payment_history)
            .filter(payment_history.user_id == user_id)
            .order_by(payment_history.created.desc())
            .all()
        )
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []