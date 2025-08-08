from db.database import db_session
from sqlalchemy import and_, or_
from collections import OrderedDict
from db.models.tradestation_instruments import TradeStationInstrument
from config import logger


def get_tradestation_instrument_by_symbol(symbol, inst_type):
    query = db_session.query(TradeStationInstrument).filter(and_(TradeStationInstrument.symbol == symbol,
                                                                  TradeStationInstrument.inst_type == inst_type))
    logger.info(f'Request to save settings data {query.statement}')
    entity = query.first()
    db_session.close()
    return entity

def get_tradestation_setting_for_user_by_local_symbol(local_symbol, inst_type, random_id=None):
    query = db_session.query(TradeStationInstrument).filter(and_(TradeStationInstrument.local_symbol == local_symbol,
                                                                  TradeStationInstrument.inst_type == inst_type),
                                                            TradeStationInstrument.random_id == random_id)
    logger.info(f'Request to save settings data {query.statement}')
    entity = query.first()
    db_session.close()
    return entity

def get_tradestation_setting_for_user_by_tradestation_symbol(local_symbol, inst_type):
    query = db_session.query(TradeStationInstrument).filter(and_(TradeStationInstrument.trade_station_symbol == local_symbol,
                                                                    TradeStationInstrument.inst_type == inst_type))
    logger.info(f'Request to save settings data {query.statement}')
    entity = query.first()
    db_session.close()
    return entity

def get_tradestation_setting_for_user_by_tradestation_symbol_user(local_symbol, inst_type, random_id):
    query = db_session.query(TradeStationInstrument).filter(and_(TradeStationInstrument.trade_station_symbol == local_symbol,
                                                                    TradeStationInstrument.inst_type == inst_type,
                                                                 TradeStationInstrument.random_id == random_id))
    logger.info(f'Request to save settings data {query.statement}')
    entity = query.first()
    db_session.close()
    return entity

def get_tradestation_setting(user, page=1, page_size=100):
    try:
        query = db_session.query(TradeStationInstrument).filter(
            or_(
                TradeStationInstrument.random_id == user.random_id,
                TradeStationInstrument.random_id.is_(None)
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
                ('Tradestation Symbol', symbol.trade_station_symbol),
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

def search_tradestation_setting(user, search_query, page=1, page_size=100, inst_type=None):
    try:
        if inst_type is None or inst_type == '':
            query = db_session.query(TradeStationInstrument).filter(
                or_(
                    TradeStationInstrument.random_id == user.random_id,
                    TradeStationInstrument.random_id.is_(None)
                ),
                TradeStationInstrument.symbol.ilike(f'%{search_query}%')  # Case-insensitive search for the symbol
            )
        else:
            query = db_session.query(TradeStationInstrument).filter(
                or_(
                    TradeStationInstrument.random_id == user.random_id,
                    TradeStationInstrument.random_id.is_(None)
                ),
                TradeStationInstrument.symbol.ilike(f'%{search_query}%'),  # Case-insensitive search for the symbol
                TradeStationInstrument.inst_type == inst_type
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
                'Tradestation Symbol': symbol.trade_station_symbol,
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

def get_unique_inst_type():
    entities = db_session.query(TradeStationInstrument).all()
    db_session.close()
    all_unqiue_inst_type = [entity.inst_type for entity in entities]
    return list(set(all_unqiue_inst_type))