import traceback

from sqlalchemy import or_, and_

from config import logger
from db.models.trade_data import trade_data
from db.database import db_session
import re

async def is_trade_exists_by_random_id(random_id: int) -> bool:
    """Check if any trade exists for the given user_random_id."""
    try:
        exists = db_session.query(trade_data).filter(trade_data.user_id == random_id).first()
        return bool(exists)
    except Exception as e:
        logger.error(f"Exception in DB operation: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return False

def get_trade_data_by_user_random_id(user_id,random_key):
    entity = db_session.query(trade_data).filter(trade_data.user_id == user_id).filter(trade_data.random_key == random_key).first()
    db_session.close()
    return entity

def get_by_trade_date_time(date_time):
    entity = db_session.query(trade_data).filter(trade_data.tradeDate == date_time.date()).count()
    db_session.close()
    return entity

def all_trades_by_user_no_trade(user_id):
    entity = db_session.query(trade_data).filter(trade_data.user_id == user_id).all()
    db_session.close()
    return entity

def all_trades_by_user(user_id):
    entity = (db_session.query(trade_data).filter(trade_data.user_id == user_id)
              .filter( and_(trade_data.status != 'StopLoss Update Done',trade_data.status != 'Position Closed',trade_data.status != 'TakeProfit Update Done' ) )
              .filter(or_(trade_data.entry_id == None,trade_data.entry_id == "")).all())
    db_session.close()
    return entity

def all_trades_by_user_entry_found(user_id):
    entity = db_session.query(trade_data).filter(trade_data.user_id == user_id).filter(and_(trade_data.entry_id != None,trade_data.entry_id != "")).all()
    db_session.close()
    return entity

def count_trade_date_time(date_time,user_id):
    entity = db_session.query(trade_data).filter(trade_data.tradeDate == date_time.date()).filter(trade_data.user_id == user_id).count()
    db_session.close()
    return entity

def trade_date_time_with_symbol(date_time,user_id,symbol):
    entity = db_session.query(trade_data).filter(trade_data.tradeDate >= date_time.date()).filter(trade_data.user_id == user_id).filter(trade_data.local_symbol == symbol).all()
    db_session.close()
    return entity

async def fetchtrade_date_time_and_symbol_and_user(date_time,symbol,user_id):
    entity = db_session.query(trade_data).filter(trade_data.trade_time == date_time).filter(trade_data.symbol == symbol).filter(trade_data.user_id == user_id).all()
    db_session.close()
    return entity

def validate_trade_date_time_and_symbol_and_user(date_time,symbol,user_id,user_account_name):
    entity = (db_session.query(trade_data).filter(trade_data.trade_time == date_time).filter(trade_data.account == user_account_name)
              .filter(trade_data.symbol == symbol).filter(trade_data.user_id == user_id).first())
    db_session.close()
    return entity

def validate_trade_date_time_and_symbol_and_user_and_key(date_time,symbol,user_id,user_account_name,random_key):
    entity = (db_session.query(trade_data).filter(trade_data.trade_time == date_time).filter(trade_data.account == user_account_name)
              .filter(trade_data.symbol == symbol).filter(trade_data.user_id == user_id).filter(trade_data.random_key == random_key).order_by(trade_data.row_id.desc()).first())
    db_session.close()
    return entity

def get_by_trade_date_time_and_symbol_and_user(date_time,symbol,user_id):
    entity = db_session.query(trade_data).filter(trade_data.trade_time == date_time).filter(trade_data.symbol == symbol).filter(trade_data.user_id == user_id).first()
    db_session.close()
    return entity

def get_tp_id_trade_date_time_and_symbol_and_user(symbol,user_id):
    entity = db_session.query(trade_data).filter(trade_data.local_symbol == symbol).filter(trade_data.user_id == user_id).filter(trade_data.lmt_id != None).all()
    db_session.close()

    return entity

def get_sl_id_trade_date_time_and_symbol_and_user(symbol,user_id):
    entity = db_session.query(trade_data).filter(trade_data.local_symbol == symbol).filter(trade_data.user_id == user_id).filter(trade_data.stp_id != None).all()
    db_session.close()
    return entity

def get_by_trade_order_id(order_id):
    entity = db_session.query(trade_data).filter(trade_data.order_id == str(order_id)).first()
    db_session.close()
    return entity



def get_by_trade_order_id_entry(order_id):
    entity = db_session.query(trade_data).filter(trade_data.entry_id == str(order_id)).order_by(trade_data.row_id.desc()).first()
    db_session.close()
    return entity
def get_by_trade_order_id_tp(order_id):
    entity = db_session.query(trade_data).filter(trade_data.lmt_id == str(order_id)).order_by(trade_data.row_id.desc()).first()
    db_session.close()
    return entity
def get_by_trade_order_id_sl(order_id):
    entity = db_session.query(trade_data).filter(trade_data.stp_id == str(order_id)).order_by(trade_data.row_id.desc()).first()
    db_session.close()
    return entity

def get_by_trade_row_id(row_id):
    entity = db_session.query(trade_data).filter(trade_data.row_id == row_id).first()
    db_session.close()
    return entity

def get_by_date_alert_details(user,from_date,to_date, engine):

    entity = db_session.query(trade_data).filter(trade_data.user_id == user.random_id).filter(trade_data.platform == engine).filter(trade_data.tradeDate >= from_date).filter(trade_data.tradeDate < to_date).all()
    db_session.close()
    return entity

def get_trade_data():
    retval = []
    for trade_data_obj in trade_data.query.all():
        retval_item = {}
        retval_item['Symbol'] = trade_data_obj.symbol
        retval_item['OrderType'] = trade_data_obj.order_type
        retval_item['Quantity'] = trade_data_obj.quantity
        retval_item['LimitOffset'] = trade_data_obj.limit_offset
        retval_item['StopOffset'] = trade_data_obj.stop_offset
        retval_item['BuySell'] = trade_data_obj.buy_sell
        retval_item['Time'] = re.sub('[\d-]+--', '', trade_data_obj.trade_time)
        retval_item['OrderStatus'] = trade_data_obj.status
        retval_item['SecurityType'] = trade_data_obj.inst_type
        retval_item['EntryOffsetInPercentage'] = trade_data_obj.EntryOffsetInPercentage
        retval_item['Exchange'] = trade_data_obj.Exchange
        retval_item['TimeInForce'] = trade_data_obj.TimeInForce
        retval_item['LocalSymbol'] = trade_data_obj.local_symbol
        retval_item['MaturityDate'] = trade_data_obj.MaturityDate
        retval.append(retval_item)
    db_session.close()
    return retval



def get_total_trade_by_id(random_id):
    entity = db_session.query(trade_data).filter(trade_data.user_id == random_id).all()
    db_session.close()
    return entity
def get_total_success_trade_by_id(random_id):
    entity = db_session.query(trade_data).filter(trade_data.user_id == random_id).filter(trade_data.entry_id != None).all()
    db_session.close()
    return entity