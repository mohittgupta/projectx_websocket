import traceback

from sqlalchemy import and_

from config import logger
from db.database import db_session
from db.models.projectx_data import Projectx_Orders


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

def get_projectx_orders_by_user_id(user_id):
    try:
        entity = db_session.query(Projectx_Orders).filter(Projectx_Orders.user_id == user_id).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in get_projectx_orders_by_user_id: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_projectx_orders_by_user_id_and_connection_name(user_id, connection_name):
    try:
        
        entity = db_session.query(Projectx_Orders).filter(
            and_(Projectx_Orders.user_id == user_id, Projectx_Orders.connection_name == connection_name)
        ).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in get_projectx_orders_by_user_id_and_connection_name: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None
    
def get_projectx_order_by_order_id(user_id, connection_name, order_id):
    try:
        
        entity = db_session.query(Projectx_Orders).filter(
            and_(Projectx_Orders.user_id == user_id,
                 Projectx_Orders.connection_name == connection_name,
                 Projectx_Orders.order_id == order_id)
        ).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in get_projectx_order_by_order_id: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_projectx_orders_by_account_id(account_id):
    try:
        
        entity = db_session.query(Projectx_Orders).filter(Projectx_Orders.account_id == account_id).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in get_projectx_orders_by_account_id: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None


def save_projectx_order(order):
    try:
        db_session.add(order)
        db_session.commit()
        db_session.close()
        return order
    except Exception as e:
        logger.error(f"Exception in save_projectx_order: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None