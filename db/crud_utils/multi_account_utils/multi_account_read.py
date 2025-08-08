import traceback

from sqlalchemy import and_

from config import logger
from db.models.multi_accounts import multi_accounts
from db.database import db_session

async def get_by_id_multi_acc(id,user_id):
    try:
        user = db_session.query(multi_accounts).filter(multi_accounts.id == id).filter(multi_accounts.user_random_id == user_id).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_by_user_id_multi_acc(user_id):
    try:
        user = db_session.query(multi_accounts).filter(multi_accounts.user_random_id == user_id).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []
async def get_by_userby_master_id(master_token):
    try:
        user = db_session.query(multi_accounts).filter(multi_accounts.master_user == master_token).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []
