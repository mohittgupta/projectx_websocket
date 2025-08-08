import json
from collections import OrderedDict

from sqlalchemy import and_, or_, cast, Integer

from config import logger
from db.database import db_session
from db.models.tradeloacker_settings import TradeLockerSetting
from utils.linetimer import timing_decorator


def get_tradelocker_setting_by_symbol_and_id(symbol, random_id=''):
    entity = db_session.query(TradeLockerSetting).filter(and_(TradeLockerSetting.symbol == symbol, TradeLockerSetting.random_id == random_id)).first()
    db_session.close()
    return entity

def get_tradelocker_setting_for_user_by_symbol_and_expiry_date(symbol, expiry_date):
    entity = (
        db_session.query(TradeLockerSetting)
        .filter(
            and_(
                TradeLockerSetting.symbol == symbol,
                cast(TradeLockerSetting.MaturityDate, Integer) >= cast(expiry_date, Integer)
            )
        )
        .order_by(cast(TradeLockerSetting.MaturityDate, Integer).asc())
        .first()
    )
    db_session.close()
    return entity

def get_tradelocker_setting_for_user_by_local_symbol(symbol, inst_type, random_id):
    query = db_session.query(TradeLockerSetting).filter(and_(TradeLockerSetting.local_symbol == symbol, TradeLockerSetting.inst_type == inst_type, TradeLockerSetting.random_id == random_id))
    #logger.info(f'Request to save settings data {query.statement}')
    entity = query.first()
    db_session.close()
    return entity

def get_tradelocker_setting_for_user_by_symbol(symbol, inst_type, random_id):
    query = db_session.query(TradeLockerSetting).filter(and_(TradeLockerSetting.symbol == symbol, TradeLockerSetting.inst_type == inst_type, TradeLockerSetting.random_id == random_id))
    #logger.info(f'Request to save settings data {query.statement}')
    entity = query.first()
    db_session.close()
    return entity

def get_tradelocker_setting_for_user_by_tradelockersymbol(symbol, inst_type, random_id):
    query = db_session.query(TradeLockerSetting).filter(and_(TradeLockerSetting.tradelocker_symbol == symbol, TradeLockerSetting.inst_type == inst_type, TradeLockerSetting.random_id == random_id))
    #logger.info(f'Request to save settings data {query.statement}')
    entity = query.first()
    db_session.close()
    return entity

def get_tradelocker_setting(user, page=1, page_size=100):
    try:
        query = db_session.query(TradeLockerSetting).filter(
            or_(
                TradeLockerSetting.random_id == user.random_id,
                TradeLockerSetting.random_id.is_(None)
            )
        )

        # Apply pagination
        offset = (page - 1) * page_size
        all_symbols = query.offset(offset).limit(page_size).all()

        retval = []
        for symbol in all_symbols:
            retval_item = OrderedDict([
                ('Local Symbol', symbol.local_symbol),
                ('Symbol', symbol.symbol),
                ('tradelocker_symbol', symbol.tradelocker_symbol),
                ('Quantity', symbol.quantity),
                ('Instrument Type', symbol.inst_type),
                ('Order Type', symbol.order_type),
                ('Exchange', symbol.Exchange),
                ('Currency', symbol.Currency),
                ('Lot Size', symbol.lot_size),
                ('Min Tick', symbol.min_tick),
            ])
            retval.append(retval_item)

        response_data = {
            "data": retval,
            "error": False,
            "page": page,
            "page_size": page_size,
            "total_items": query.count()
        }

        # Manually serialize the data into JSON with OrderedDict
        # response_json = json.dumps(response_data, indent=4)
        return response_data
    finally:
        db_session.close()

def search_tradelocker_settings(user, search_query, page=1, page_size=100, inst_type=None):
    try:
        if inst_type is None or inst_type == '':
            query = db_session.query(TradeLockerSetting).filter(
                or_(
                    TradeLockerSetting.random_id == user.random_id,
                    TradeLockerSetting.random_id.is_(None)
                ),
                TradeLockerSetting.symbol.ilike(f'%{search_query}%')  # Case-insensitive search for the symbol
            )
        else:
            query = db_session.query(TradeLockerSetting).filter(
                or_(
                    TradeLockerSetting.random_id == user.random_id,
                    TradeLockerSetting.random_id.is_(None)
                ),
                TradeLockerSetting.symbol.ilike(f'%{search_query}%'),  # Case-insensitive search for the symbol
                TradeLockerSetting.inst_type == inst_type
            )

        # Apply pagination
        offset = (page - 1) * page_size
        all_symbols = query.offset(offset).limit(page_size).all()

        retval = []
        for symbol in all_symbols:
            retval_item = {
                'Local Symbol': symbol.local_symbol,
                'Quantity': symbol.quantity,
                'Instrument Type': symbol.inst_type,
                'Order Type': symbol.order_type,
                'Exchange': symbol.Exchange,
                'Symbol': symbol.symbol,
                'Tradelocker Symbol': symbol.tradelocker_symbol,
                'Currency': symbol.Currency,
                'Lot Size': symbol.lot_size,
                'Min Tick': symbol.min_tick,
                'Strike Price Interval': symbol.strike_price_interval,
                'Isin': symbol.isin,
                'Cusip': symbol.cusip,
            }
            retval.append(retval_item)

        return {
            "data": retval,
            "error": False,
            "page": page,
            "page_size": page_size,
            "total_items": query.count()
        }
    finally:
        db_session.close()


def get_instrument_data_using_con_id(con_id):
    entity = db_session.query(TradeLockerSetting).filter(TradeLockerSetting.con_id == con_id).first()
    db_session.close()
    return entity

def get_all_inst_unique_inst_type():
    entities = db_session.query(TradeLockerSetting).all()
    db_session.close()
    all_unqiue_inst_type = [entity.inst_type for entity in entities]
    return list(set(all_unqiue_inst_type))

def get_tradelocker_setting_for_user_by_local_symbol_server(symbol, inst_type, random_id, server):
    query = db_session.query(TradeLockerSetting).filter(and_(TradeLockerSetting.local_symbol == symbol, TradeLockerSetting.inst_type == inst_type, TradeLockerSetting.random_id == random_id, TradeLockerSetting.server == server))
    #logger.info(f'Request to save settings data {query.statement}')
    entity = query.first()
    db_session.close()
    return entity