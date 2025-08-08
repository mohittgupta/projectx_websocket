import traceback

from config import logger
from db.database import db_session
from db.models.rollover_data import rollover_data


async def get_all_rollover_db_data():
    try:
        entity = db_session.query(rollover_data).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []


async def get_all_rollover_db_data_by_root(symbol,exchange):
    try:
        entity = db_session.query(rollover_data).filter(rollover_data.root_symbol == symbol).filter(rollover_data.exchange == exchange).order_by(rollover_data.id.asc()).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def delete_all_rollover_db_data():
    try:
        entity = db_session.query(rollover_data).delete()
        db_session.commit()
        db_session.close()
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()