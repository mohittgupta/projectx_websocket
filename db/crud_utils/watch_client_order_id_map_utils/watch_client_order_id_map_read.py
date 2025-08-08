import traceback

from sqlalchemy import and_

from config import logger
from db.models.watch_client_order_id_map import watch_client_order_id_map
from db.database import db_session

async def get_wast_map_by_master_order_id_token(master_token,order_id , client_id):
    try:
        entity = (db_session.query(watch_client_order_id_map).filter(watch_client_order_id_map.master_order_id == str(order_id))
                  .filter(watch_client_order_id_map.child_token == str(client_id)).filter(watch_client_order_id_map.master_token == str(master_token)).all())
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []
async def get_wast_map_by_order_id_token(order_id):
    try:
        entity = db_session.query(watch_client_order_id_map).filter(watch_client_order_id_map.master_order_id == str(order_id)).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_wast_map_by_master_token(token,from_date,to_date):
    try:
        entity = db_session.query(watch_client_order_id_map).filter(watch_client_order_id_map.master_token == token).filter(and_(watch_client_order_id_map.datetime >= from_date,watch_client_order_id_map.datetime <= to_date)).order_by(watch_client_order_id_map.id.desc()).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []