import json
from collections import OrderedDict

from sqlalchemy import and_, or_, cast, Integer

from db.database import db_session
from db.models.ib_trade_setting import IBTradeSetting
from db.models.ib_meta_data import IBMetaData




def get_projectx_settings_for_user_by_local_symbol(symbol, inst_type, random_id):
    query = db_session.query(IBTradeSetting).filter(and_(IBTradeSetting.local_symbol == symbol, IBTradeSetting.inst_type == inst_type, IBTradeSetting.random_id == random_id, IBTradeSetting.projectx_id.isnot(None)))
    entity = query.first()
    db_session.close()
    return entity

def get_projectx_settings_for_user_by_local_symbol_x(symbol, inst_type, random_id):
    query = db_session.query(IBTradeSetting).filter(and_(IBTradeSetting.local_symbol == symbol, IBTradeSetting.inst_type == inst_type, IBTradeSetting.random_id == random_id, IBTradeSetting.projectx_id.isnot(None)))
    entity = query.first()
    db_session.close()
    return entity

def get_projectx_settings_for_user_by_symbol(symbol, inst_type, random_id):
    query = db_session.query(IBTradeSetting).filter(and_(IBTradeSetting.symbol == symbol, IBTradeSetting.inst_type == inst_type, IBTradeSetting.random_id == random_id, IBTradeSetting.projectx_id.isnot(None)))
    entity = query.first()
    db_session.close()
    return entity



def get_all_ib_trade_meta_data_for_user_by_symbol(symbol, expiry_date, inst_type):

    entity = (
        db_session.query(IBMetaData)
        .filter(
            and_(
                IBMetaData.symbol == symbol,
                IBMetaData.inst_type == inst_type,
                cast(IBMetaData.maturity_date, Integer) >= cast(expiry_date, Integer)
            )
        )
        .order_by(cast(IBMetaData.maturity_date, Integer).asc())
        .all()
    )
    db_session.close()
    return entity

def get_projectx_setting(user, page=1, page_size=100):
    try:
        query = db_session.query(IBTradeSetting).filter(
            or_(

                IBTradeSetting.random_id == user.random_id,
                IBTradeSetting.random_id.is_(None)
            ), IBTradeSetting.inst_type=='FUT',
            IBTradeSetting.projectx_id.isnot(None)
        )

        # Apply pagination
        offset = (page - 1) * page_size
        all_symbols = query.offset(offset).limit(page_size).all()

        retval = []
        for symbol in all_symbols:
            retval_item = OrderedDict([
                ('Local Symbol', symbol.local_symbol),
                ('Symbol', symbol.symbol),
                ('Quantity', symbol.quantity),
                ('Instrument Type', symbol.inst_type),
                ('Order Type', symbol.order_type),
                ('Exchange', symbol.Exchange),
                ('Currency', symbol.Currency),
                ('Lot Size', symbol.lot_size),
                ('Min Tick', symbol.min_tick),
                ('ProjectX Symbol ID', symbol.projectx_id)
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

def search_projectx_settings(user, search_query, page=1, page_size=100, inst_type=None):
    try:
        if inst_type is None or inst_type == '':
            query = db_session.query(IBTradeSetting).filter(
                or_(
                    IBTradeSetting.random_id == user.random_id,
                    IBTradeSetting.random_id.is_(None)
                ),IBTradeSetting.inst_type=='FUT',
            IBTradeSetting.projectx_id.isnot(None),
                IBTradeSetting.symbol.ilike(f'%{search_query}%')  # Case-insensitive search for the symbol
            )
        else:
            query = db_session.query(IBTradeSetting).filter(
                or_(
                    IBTradeSetting.random_id == user.random_id,
                    IBTradeSetting.random_id.is_(None)
                ),
                IBTradeSetting.inst_type == 'FUT',
                IBTradeSetting.projectx_id.isnot(None),
                IBTradeSetting.symbol.ilike(f'%{search_query}%'),  # Case-insensitive search for the symbol
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
                'Currency': symbol.Currency,
                'Lot Size': symbol.lot_size,
                'Min Tick': symbol.min_tick,
                'Strike Price Interval': symbol.strike_price_interval,
                'ProjectX Symbol ID': symbol.projectx_id
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

def get_ib_trade_setting_for_user_by_local(symbol, inst_type):
    query = db_session.query(IBTradeSetting).filter(and_(IBTradeSetting.local_symbol == symbol, IBTradeSetting.inst_type == inst_type))
    entity = query.first()
    db_session.close()
    return entity

def get_ib_trade_setting_for_user_by_projectx_id(projectx_id):
    query = db_session.query(IBTradeSetting).filter(
        and_(
            IBTradeSetting.projectx_id == projectx_id
        )
    )
    entity = query.first()
    db_session.close()
    return entity
