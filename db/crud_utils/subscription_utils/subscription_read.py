import traceback

from sqlalchemy import or_

from config import logger
from db.models.subscription_init import subscription_init
from db.database import db_session
import re

async def get_by_subscription_order_id(order_id):
    try:
        entity = db_session.query(subscription_init).filter(subscription_init.subscription_id == order_id).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_by_subscription_paddel_subs_id(order_id):
    try:
        entity = db_session.query(subscription_init).filter(subscription_init.paddle_sub_id == order_id).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_last_active_subscription(mail):
    try:
        entity = db_session.query(subscription_init).filter(subscription_init.email == mail).filter(subscription_init.status == 'Subscription Activated').order_by(subscription_init.id.desc()).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_last_active_subscription_sub_id(mail,sub_id):
    try:
        entity = db_session.query(subscription_init).filter(subscription_init.email == mail).filter(subscription_init.subscription_id == sub_id).filter(subscription_init.status == 'Subscription Activated').order_by(subscription_init.id.desc()).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None
async def get_all_active_subscription(mail):
    try:
        entity = db_session.query(subscription_init).filter(subscription_init.email == mail).filter(subscription_init.status == 'Subscription Activated').all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_last_active_or_created_subscription(mail):
    try:
        entity = db_session.query(subscription_init).filter(subscription_init.email == mail).order_by(subscription_init.id.desc()).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None
async def get_by_subscriptions_by_email(email):
    try:
        entity = db_session.query(subscription_init).filter(subscription_init.email == email).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_created_only():
    try:
        entity = db_session.query(subscription_init).filter(subscription_init.status == 'Created').filter(or_(subscription_init.mail_send ==None,subscription_init.mail_send == False)).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_active_manual_Cancelled_subscription():
    try:
        entity = db_session.query(subscription_init).filter(or_(subscription_init.status == 'Subscription Activated',subscription_init.status == 'MANUAL CANCELLED')).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

def get_all_active_subscription(mail):
    entity = db_session.query(subscription_init).filter(subscription_init.email == mail).filter(subscription_init.status == 'Subscription Activated').order_by(subscription_init.id.desc()).all()
    db_session.close()
    return entity

def get_all_subscription():
    entity = db_session.query(subscription_init).filter(subscription_init.status == 'Subscription Activated').order_by(subscription_init.id.desc()).all()
    db_session.close()
    return entity