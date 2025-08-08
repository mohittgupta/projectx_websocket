import traceback

from config import logger
from db.database import db_session
from db.models.manual_trade_pause import manual_trade_pause


async def get_by_user_id_manual_trade_pause(user_key):
    try:
        entity = db_session.query(manual_trade_pause).filter(manual_trade_pause.user_id == user_key).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None



async def get_all_by_user_id_manual_trade_pause(user_key):
    try:
        entity = db_session.query(manual_trade_pause).filter(manual_trade_pause.user_id == user_key).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_all_by_id_user_id_manual_trade_pause(user_id,id):
    try:
        entity = db_session.query(manual_trade_pause).filter(manual_trade_pause.user_id == user_id).filter(manual_trade_pause.row_id == id).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None