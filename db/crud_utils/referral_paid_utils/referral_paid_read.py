import traceback

from sqlalchemy import and_

from config import logger
from db.models.referral_paid import referral_paid
from db.database import db_session

async def get_all_paid_referal():
    try:
        entity = db_session.query(referral_paid).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []
async def get_all_paid_referal_by_code(referral_code):
    try:
        entity = db_session.query(referral_paid).filter(referral_paid.referral_code == referral_code).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_all_paid_referral_by_user_id(user_id) -> list[referral_paid]:
    try:
        entity = db_session.query(referral_paid).filter(referral_paid.user_id == user_id).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []