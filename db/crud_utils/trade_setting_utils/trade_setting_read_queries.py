import json
import traceback

from sqlalchemy import and_, or_

from config import logger
from db.models.trade_setting import trade_setting
from db.database import db_session


def get_setting_by_symbol(symbol):
    entity = db_session.query(trade_setting).filter(trade_setting.symbol == symbol).first()
    db_session.close()
    return entity


def get_setting_by_random_id(random_id):
    entity = db_session.query(trade_setting).filter(trade_setting.random_id == random_id).all()
    db_session.close()
    return entity


async def get_symbol_setting(random_id, symbol):
    entity = db_session.query(trade_setting).filter(
        and_(trade_setting.symbol == symbol, trade_setting.random_id == random_id)).first()
    db_session.close()
    return entity


def get_localsymbol_setting(random_id, localsymbol, continuous_symbol):
    entity = db_session.query(trade_setting).filter(
        and_(trade_setting.local_symbol == localsymbol, trade_setting.random_id == random_id,
             trade_setting.symbol != continuous_symbol)).first()
    db_session.close()
    return entity


def get_setting_by_symbol_and_id(symbol, random_id):
    entity = db_session.query(trade_setting).filter(
        and_(trade_setting.symbol == symbol, trade_setting.random_id == random_id)).first()
    db_session.close()
    return entity


def get_setting_for_use_by_symbol(symbol):
    entity = db_session.query(trade_setting).filter(trade_setting.symbol == symbol).first()
    db_session.close()
    if entity is None:
        entity = db_session.query(trade_setting).filter(trade_setting.symbol == 'COMMON').first()
        db_session.close()
    return entity


def get_setting_for_use_by_symbol_and_user(symbol, random_id):
    entity = db_session.query(trade_setting).filter(
        and_(trade_setting.symbol == symbol, trade_setting.random_id == random_id)).first()
    db_session.close()
    if entity is None:
        entity = db_session.query(trade_setting).filter(
            and_(trade_setting.symbol == 'COMMON', trade_setting.random_id == random_id)).first()
        db_session.close()
    return entity


def get_setting_for_use_by_rithmic_symbol_and_user(symbol, random_id):
    entity = db_session.query(trade_setting).filter(
        and_(trade_setting.local_symbol == symbol, trade_setting.random_id == random_id)).first()
    db_session.close()
    if entity is None:
        entity = db_session.query(trade_setting).filter(
            and_(trade_setting.symbol == 'COMMON', trade_setting.random_id == random_id)).first()
        db_session.close()
    return entity

def get_settings(user, page=1, page_size=100):
    try:
        query = db_session.query(trade_setting).filter(
            or_(
                trade_setting.random_id == None,
                trade_setting.random_id == user.random_id
            )
        )

        total_items = query.count()

        if page_size * page > total_items:
            page = 1

        # Apply pagination
        offset = (page - 1) * page_size
        data = query.offset(offset).limit(page_size).all()

        retval = []
        for settings in data:
            retval_item = {
                'Symbol': settings.symbol,
                'Order Type': settings.order_type,
                'Quantity': settings.quantity,
                'Rithmic Symbol': settings.local_symbol,
                'Lot Size': settings.lot_size,
                'Min Tick': settings.min_tick,
                'Exchange': settings.Exchange,
                'Manual Change': settings.manualchange,
                'Entry Offset': settings.eEntryOffset,
            }
            retval.append(retval_item)

        response_data = {
            "data": retval,
            "error": False,
            "page": page,
            "page_size": page_size,
            "total_items": total_items
        }

        return response_data
    except Exception as e:
        logger.info(f'Error traceback: {traceback.format_exc()}')
    finally:
        db_session.close()



def search_rithmic_settings(user, search_query, page=1, page_size=100, inst_type=None):
    try:
        if inst_type is None or inst_type == '':
            query = db_session.query(trade_setting).filter(
                trade_setting.random_id == user.random_id,
                trade_setting.symbol.like(f'%{search_query}%')  # Case-insensitive search for the symbol
            )
        else:
            query = db_session.query(trade_setting).filter(
                trade_setting.random_id == user.random_id,
                trade_setting.symbol.like(f'%{search_query}%'),  # Case-insensitive search for the symbol
                trade_setting.inst_type == inst_type
            )


        # Apply pagination
        offset = (page - 1) * page_size
        data = query.offset(offset).limit(page_size).all()
        if page == 1 and len(data) == 0:
            if inst_type is None or inst_type == '':
                query = db_session.query(trade_setting).filter(
                    trade_setting.random_id == None,
                    trade_setting.symbol.like(f'%{search_query}%')  # Case-insensitive search for the symbol
                )
            else:
                query = db_session.query(trade_setting).filter(
                    trade_setting.random_id == None,
                    trade_setting.symbol.like(f'%{search_query}%'),  # Case-insensitive search for the symbol
                    trade_setting.inst_type == inst_type
                )

            # Apply pagination
            offset = (page - 1) * page_size
            data = query.offset(offset).limit(page_size).all()

        retval = []
        for settings in data:
            retval_item = {
                'Symbol': settings.symbol,
                'Order Type': settings.order_type,
                'Quantity': settings.quantity,
                'Rithmic Symbol': settings.local_symbol,
                'Lot Size': settings.lot_size,
                'Min Tick': settings.min_tick,
                'Exchange': settings.Exchange,
                'Manual Change': settings.manualchange,
                'Entry Offset': settings.eEntryOffset,
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
