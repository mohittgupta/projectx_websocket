import traceback

from config import logger
from db.database import db_session
from db.models.manual_trade_pause_accounts import manual_trade_pause_accounts





async def get_accounts_by_user_id_trade_pause_timing(user_key,id):
    try:
        entity = db_session.query(manual_trade_pause_accounts).filter(manual_trade_pause_accounts.user_id == user_key).filter(manual_trade_pause_accounts.timming_row_id == id).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []




async def get_trade_pause_timing_for_closing():
    try:
        entity = db_session.query(manual_trade_pause_accounts).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []