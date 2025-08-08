
import traceback

from sqlalchemy import and_

from config import logger
from db.models.permission import permission
from db.database import db_session

async def get_user_permission_admin_and_slave(admin_id,slave_id):
    try:
        entity = db_session.query(permission).filter(permission.master_account == admin_id).filter(permission.slave_account == slave_id).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None



async def get_user_permission_as_admin(id):
    try:
        entity = db_session.query(permission).filter(permission.master_account == id).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_user_permission_by_request_token(id,request_token):
    try:
        entity = db_session.query(permission).filter(permission.slave_account == id).filter(permission.request_token == request_token).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_user_permission_as_salve(id):
    try:
        entity = db_session.query(permission).filter(permission.slave_account == id).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []