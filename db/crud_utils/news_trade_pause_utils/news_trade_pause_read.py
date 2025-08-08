import traceback

from sqlalchemy import and_, or_

from config import logger
from db.models.news_trade_pause import news_trade_pause
from db.database import db_session

async def get_by_user_id_news_pause_data(user_id):
    try:
        entity = db_session.query(news_trade_pause).filter(news_trade_pause.user_id == user_id).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None
async def getting_all_news_pause_data(user_id):
    try:
        entity = db_session.query(news_trade_pause).filter(news_trade_pause.user_id == user_id).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []
async def getting_all_news_pause_data_without_user():
    try:
        entity = db_session.query(news_trade_pause).filter(news_trade_pause.closed_position_open_order == True).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []