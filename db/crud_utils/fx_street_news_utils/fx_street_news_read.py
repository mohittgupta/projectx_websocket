import traceback

from sqlalchemy import and_

from config import logger
from db.models.fx_street_news import fx_street_news
from db.database import db_session

async def get_all_news_time_based(from_date,to_date):
    try:
        entity = db_session.query(fx_street_news).filter(fx_street_news.start_date >= from_date).filter(fx_street_news.start_date <= to_date).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_all_news_current_time_based(from_date):
    try:
        entity = db_session.query(fx_street_news).filter(fx_street_news.start_date == from_date).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_all_news_by_country(country):
    try:
        entity = db_session.query(fx_street_news).filter(fx_street_news.country == country).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []