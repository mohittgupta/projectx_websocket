import traceback

from sqlalchemy import and_

from config import logger
from db.models.news_symbol_mapping import news_symbol_mapping
from db.database import db_session

async def get_by_tradovate_symbol_mapping(tradovate_root):
    try:
        entity = db_session.query(news_symbol_mapping).filter(news_symbol_mapping.tradovate_root_symbol == tradovate_root).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None
async def getting_all_news_symbol_map():
    try:
        entity = db_session.query(news_symbol_mapping).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []