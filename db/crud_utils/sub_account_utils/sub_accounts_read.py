import logging
import traceback

from sqlalchemy import and_, or_

from config import logger
from db.models.sub_accounts import sub_accounts
from db.database import db_session


async def get_sub_accounts_with_mail_id(id,mail):
    try:
        user = db_session.query(sub_accounts).filter(sub_accounts.main_user_id == id).filter(sub_accounts.mail == mail).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_total_sub_accounts(id):
    try:
        user = db_session.query(sub_accounts).filter(sub_accounts.main_user_id == id).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_sub_account(mail):
    try:
        user = db_session.query(sub_accounts).filter(sub_accounts.mail == mail).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None