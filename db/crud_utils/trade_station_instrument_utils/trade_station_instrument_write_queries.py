import traceback

from utils.tradestation_utils import check_instrument_exists
from config import logger
from db.crud_utils.trade_station_instrument_utils.trade_station_instrument_read_queries import \
    get_tradestation_setting_for_user_by_tradestation_symbol_user, get_tradestation_setting_for_user_by_local_symbol, \
    get_tradestation_instrument_by_symbol
from db.database import db_session
from db.models.tradestation_instruments import TradeStationInstrument


def add_trade_station_instrument(e):
    try:
        db_session.add(e)
        db_session.commit()
        db_session.close()
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()

def tradestation_delete(symbol,user, inst_type):
    if symbol== 'COMMON':
        return {"data": f"Can Not Delete Common Setting", "error": True}
    settings_for_sym = get_tradestation_setting_for_user_by_tradestation_symbol_user(symbol, inst_type, user.random_id)
    if settings_for_sym is None:
        return {"data": f"Can't delete default setting", "error": True}
    else:
        db_session.delete(settings_for_sym)
        db_session.commit()
        db_session.close()
        return {"data": f"Successfully Delete", "error": False}

def save_tradestation_setting_by_random_id(settings ,user):
    try:
        check_server = False
        status = False
        resp = None
        random_id = user.random_id
        new_symbol_settings = None

        settings_for_sym = get_tradestation_setting_for_user_by_local_symbol(settings['LocalSymbol'], settings['SecurityType'], None)

        if settings_for_sym is None:
            settings_for_sym = get_tradestation_setting_for_user_by_tradestation_symbol_user(settings['Symbol'], settings['SecurityType'], None)

        if settings_for_sym is None:
            check_server = True
            status , resp = check_instrument_exists(settings['LocalSymbol'], user)

        if settings_for_sym is None and check_server is True and status is False:
            return {"data": f"Symbol Not Found in Tradestation Server", "error": True}

        elif settings_for_sym is not None:
            new_symbol_settings = TradeStationInstrument()


            new_symbol_settings.random_id = random_id
            new_symbol_settings.local_symbol = settings.get('LocalSymbol', settings_for_sym.local_symbol).upper()
            new_symbol_settings.inst_type = settings.get('SecurityType', settings_for_sym.inst_type).upper()
            new_symbol_settings.order_type = settings.get('OrderType', settings_for_sym.order_type).upper()
            new_symbol_settings.Exchange = settings.get('Exchange', settings_for_sym.Exchange).upper()
            new_symbol_settings.symbol = settings.get('Symbol', settings_for_sym.symbol).upper()
            new_symbol_settings.con_id = settings.get('con_id', settings_for_sym.con_id)
            new_symbol_settings.trade_station_symbol = settings.get('symbol', settings_for_sym.trade_station_symbol).upper()
            new_symbol_settings.Currency = settings.get('Currency', settings_for_sym.Currency).upper()
            new_symbol_settings.lot_size = settings.get('LotSize', settings_for_sym.lot_size)
            new_symbol_settings.min_tick = settings.get('MinTick', settings_for_sym.min_tick)
            new_symbol_settings.strike_price_interval = settings.get('strike_price_interval', settings_for_sym.strike_price_interval)
            new_symbol_settings.isin = settings.get('isin', settings_for_sym.isin)
            new_symbol_settings.quantity = settings.get('quantity', settings_for_sym.quantity)
            new_symbol_settings.cusip = settings.get('cusip', settings_for_sym.cusip)
            db_session.add(new_symbol_settings)
            db_session.commit()
            db_session.close()

            return {"data": f"Successfully Saved", "error": False}
        elif settings_for_sym is None and check_server is True and status is True:
            new_symbol_settings = TradeStationInstrument()
            api_category = resp.get("Category")
            if api_category == "Future":
                api_category = "Futures"

            new_symbol_settings.random_id = random_id
            new_symbol_settings.local_symbol = settings.get('LocalSymbol').upper()
            new_symbol_settings.inst_type = settings.get('SecurityType', api_category).upper()
            new_symbol_settings.order_type = settings.get('OrderType').upper()
            new_symbol_settings.Exchange = resp['Exchange']
            new_symbol_settings.symbol = settings.get('Symbol').upper()
            new_symbol_settings.con_id = None
            new_symbol_settings.trade_station_symbol = settings.get('LocalSymbol').upper()
            new_symbol_settings.Currency = settings.get('Currency', resp['Currency']).upper()
            new_symbol_settings.lot_size = settings.get('LotSize', resp['LotSize'])
            new_symbol_settings.min_tick = settings.get('MinTick', resp['MinMove'])
            new_symbol_settings.strike_price_interval = None
            new_symbol_settings.isin = ''
            new_symbol_settings.quantity = settings.get('quantity', 1)
            new_symbol_settings.cusip = ''

            db_session.add(new_symbol_settings)
            db_session.commit()
            db_session.close()

            return {"data": f"Successfully Saved", "error": False}
    except Exception as e:
        logger.error(f"error in save setting {traceback.format_exc()}")
        return {"data" :f"Error in Setting Data {e}" ,"error" :True}