import traceback

from sqlalchemy import and_

from config import logger
from db.database import db_session
from db.models.projectx_data import Projectx_Positions


# async def get_by_code_discount_order(code):
#     try:
#         entity = db_session.query(discount).filter(discount.code == code).first()
#         db_session.close()
#         return entity
#     except Exception as e:
#         logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
#         db_session.rollback()
#         db_session.close()
#         return None


def get_projectx_positions_by_user_id(user_id):
    try:
        entity = db_session.query(Projectx_Positions).filter(Projectx_Positions.user_id == user_id).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in get_projectx_positions_by_user_id: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None


def get_projectx_positions_by_user_id_and_connection_name(user_id, connection_name):
    try:
        entity = db_session.query(Projectx_Positions).filter(
            and_(Projectx_Positions.user_id == user_id, Projectx_Positions.connection_name == connection_name)
        ).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in get_projectx_positions_by_user_id_and_connection_name: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_projectx_position_by_position_id(user_id, connection_name, position_id):
    try:
        entity = db_session.query(Projectx_Positions).filter(
            and_(Projectx_Positions.user_id == user_id,
                 Projectx_Positions.connection_name == connection_name,
                 Projectx_Positions.position_id == position_id)
        ).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in get_projectx_position_by_position_id: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_projectx_positions_by_account_id(user_id, connection_name, account_id):
    try:
        entity = db_session.query(Projectx_Positions).filter(
            and_(Projectx_Positions.user_id == user_id,
                 Projectx_Positions.connection_name == connection_name,
                 Projectx_Positions.account_id == account_id)
        ).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in get_projectx_positions_by_account_id: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def save_projectx_position(position):
    try:
        db_session.add(position)
        db_session.commit()
        db_session.close()
        return position
    except Exception as e:
        logger.error(f"Exception in save_projectx_position: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None