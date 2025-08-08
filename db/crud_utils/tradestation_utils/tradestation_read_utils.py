import traceback

from config import logger
from db.models.payment_init import payment_init
from db.database import db_session
import re

from db.models.tradestation_orders import trade_station_orders, trade_station_positions


def get_tradestation_order_by_id(user_id , order_id):
    try:
        entity = db_session.query(trade_station_orders).filter(trade_station_orders.order_id == order_id).filter(trade_station_orders.user_id == user_id).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_tradestation_order_by_account_symbol_inst_type(user_id , account_id , symbol , inst_type, status: list):
    try:
        entity = db_session.query(trade_station_orders).filter(trade_station_orders.account_id == account_id).filter(trade_station_orders.symbol == symbol).filter(trade_station_orders.user_id == user_id).filter(trade_station_orders.status.in_(status)).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_tradestation_order_for_options_by_account_symbol_inst_type(user_id , account_id , symbol , inst_type, status: list):
    try:
        entity = db_session.query(trade_station_orders).filter(trade_station_orders.account_id == account_id).filter(trade_station_orders.symbol.like(f"{symbol}%")).filter(trade_station_orders.user_id == user_id).filter(trade_station_orders.status.in_(status)).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_tradestation_position_by_id(user_id, position_id):
    try:
        entity = db_session.query(trade_station_positions).filter(trade_station_positions.position_id == position_id).filter(trade_station_orders.user_id == user_id).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_tradestation_position_by_account_symbol_inst_type(user_id , account_id , symbol , inst_type):
    try:
        entity = db_session.query(trade_station_positions).filter(trade_station_positions.account_id == account_id).filter(trade_station_positions.symbol == symbol).filter(trade_station_positions.user_id == user_id).filter(trade_station_positions.status == True).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_tradestation_position_for_options_by_account_symbol_inst_type(user_id , account_id , symbol , inst_type):
    try:
        entity = db_session.query(trade_station_positions).filter(trade_station_positions.account_id == account_id).filter(trade_station_positions.symbol.like(f"{symbol}%")).filter(trade_station_positions.user_id == user_id).filter(trade_station_positions.status == True).all()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None