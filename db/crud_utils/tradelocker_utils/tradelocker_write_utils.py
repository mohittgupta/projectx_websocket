import traceback

from tradelocker import TLAPI

from config import logger
from db.crud_utils.multi_user_connection_utils.multi_user_read_utils import get_multi_user_engine_and_user_id
from db.crud_utils.tradelocker_utils.tradeloacker_read_utils import get_tradelocker_setting_for_user_by_local_symbol, \
    get_tradelocker_setting_for_user_by_symbol, get_tradelocker_setting_for_user_by_tradelockersymbol, \
    get_tradelocker_setting_for_user_by_local_symbol_server
from db.database import db_session
from db.models.tradeloacker_settings import TradeLockerSetting



def save_tradelocker_setting_by_random_id(settings ,user):
    try:
        random_id = user.random_id
        new_symbol_settings = None
        check_server = False
        status = False
        resp = None
        settings_for_sym = get_tradelocker_setting_for_user_by_local_symbol(settings['LocalSymbol'], settings['SecurityType'], None)

        if settings_for_sym is None:
            settings_for_sym = get_tradelocker_setting_for_user_by_symbol(settings['Symbol'], settings['SecurityType'], None)

        if settings_for_sym is None:
            check_server = True
            status, resp = check_and_get_tradelocker_symbol(user, settings['Symbol'], settings['SecurityType'])



        if settings_for_sym is None and check_server is True and status is False:
            return {"data": f"Symbol Not Found in Tradestation Server", "error": True}

        elif settings_for_sym is not None:
            new_symbol_settings = TradeLockerSetting()
            new_symbol = settings_for_sym.symbol
            new_symbol_settings.random_id = random_id
            new_symbol_settings.local_symbol = settings.get('LocalSymbol', settings_for_sym.local_symbol).upper()
            new_symbol_settings.inst_type = settings.get('SecurityType', settings_for_sym.inst_type).upper()
            new_symbol_settings.order_type = settings.get('OrderType', settings_for_sym.order_type).upper()
            new_symbol_settings.Exchange = settings.get('Exchange', settings_for_sym.Exchange).upper()
            new_symbol_settings.symbol = settings.get('Symbol', new_symbol).upper()
            new_symbol_settings.con_id = settings.get('con_id', settings_for_sym.con_id)
            new_symbol_settings.tradelocker_symbol = settings.get('tradelocker_symbol', settings_for_sym.tradelocker_symbol).upper()
            new_symbol_settings.Currency = settings.get('Currency', settings_for_sym.Currency).upper()
            new_symbol_settings.lot_size = settings.get('LotSize', settings_for_sym.lot_size)
            new_symbol_settings.min_tick = settings.get('MinTick', settings_for_sym.min_tick)
            new_symbol_settings.strike_price_interval = settings.get('strike_price_interval', settings_for_sym.strike_price_interval)
            new_symbol_settings.isin = settings.get('isin', settings_for_sym.isin)
            new_symbol_settings.quantity = settings.get('quantity', settings_for_sym.quantity)
            new_symbol_settings.cusip = settings.get('cusip', settings_for_sym.cusip)
            new_symbol_settings.route = settings.get('route', settings_for_sym.route)
            new_symbol_settings.server = settings.get('server', settings_for_sym.server)
            db_session.add(new_symbol_settings)
            db_session.commit()
            db_session.close()

            return {"data": f"Successfully Saved", "error": False}
        elif settings_for_sym is None and check_server is True and status is True:
            new_save_tradelocker_setting(resp, user)
            return {"data": f"Successfully Saved", "error": False}
    except Exception as e:
        logger.error(f"error in save setting {traceback.format_exc()}")
        return {"data" :f"Error in Setting Data {e}" ,"error" :True}

def save_tradelocker_setting(settings, server=None):
    try:

        new_symbol_settings = None
        if server is None:
            settings_for_sym = get_tradelocker_setting_for_user_by_local_symbol(settings['LocalSymbol'], settings['SecurityType'], None)

            if settings_for_sym is None:
                settings_for_sym = get_tradelocker_setting_for_user_by_symbol(settings['Symbol'], settings['SecurityType'], None)

            if settings_for_sym:
                return {"data": f"Symbol Already Exists", "error": True}
        if server:
        #     get_tradelocker_setting_for_user_by_local_symbol_server(symbol, inst_type, random_id, server)
            settings_for_sym = get_tradelocker_setting_for_user_by_local_symbol_server(settings['LocalSymbol'], settings['SecurityType'], None, server)
        if settings_for_sym is None:
            settings_for_sym = get_tradelocker_setting_for_user_by_local_symbol_server(settings['Symbol'], settings['SecurityType'], None, server)
            if settings_for_sym:
                return {"data": f"Symbol Already Exists", "error": True}

        new_symbol_settings = TradeLockerSetting()

        new_symbol_settings.local_symbol = settings.get('LocalSymbol').upper()
        new_symbol_settings.inst_type = settings.get('SecurityType').upper()
        new_symbol_settings.order_type = settings.get('OrderType').upper()
        new_symbol_settings.Exchange = settings.get('Exchange').upper()
        new_symbol_settings.symbol = settings.get('Symbol').upper()
        new_symbol_settings.con_id = settings.get('con_id')
        new_symbol_settings.tradelocker_symbol = settings.get('tradelocker_symbol').upper()
        new_symbol_settings.Currency = settings.get('Currency').upper()
        new_symbol_settings.lot_size = settings.get('LotSize')
        new_symbol_settings.min_tick = settings.get('MinTick')
        new_symbol_settings.strike_price_interval = settings.get('strike_price_interval')
        new_symbol_settings.isin = settings.get('isin')
        new_symbol_settings.quantity = settings.get('quantity')
        new_symbol_settings.route = settings.get('route')
        new_symbol_settings.server = settings.get('server', None)
        db_session.add(new_symbol_settings)
        db_session.commit()
        db_session.close()

        return {"data": f"Successfully Saved", "error": False}
    except Exception as e:
        logger.error(f"error in save setting {traceback.format_exc()}")
        return {"data" :f"Error in Setting Data {e}" ,"error" :True}

def tradelocker_delete(symbol,user, inst_type):
    if symbol== 'COMMON':
        return {"data": f"Can Not Delete Common Setting", "error": True}
    settings_for_sym = get_tradelocker_setting_for_user_by_tradelockersymbol(symbol, inst_type, user.random_id)
    if settings_for_sym is None:
        return {"data": f"Can't delete default setting", "error": True}
    else:
        db_session.delete(settings_for_sym)
        db_session.commit()
        db_session.close()
        return {"data": f"Successfully Delete", "error": False}

def check_and_get_tradelocker_symbol(user, symbol, inst_type):
    try:
        all_connections = get_multi_user_engine_and_user_id(engine='TRADELOCKER', user_id=user.id)
        if not all_connections:
            return False, None
        for connection in all_connections:
            try:
                tl = TLAPI(
                    environment=connection.connection_environment,
                    username=connection.connection_username,
                    password=connection.connection_password,
                    server=connection.connection_server
                )

                if tl is None:
                    return False , None
                all_instruments_df = tl.get_all_instruments()
                all_instruments = all_instruments_df.to_dict(orient='records')
                same_instrument = [instrument for instrument in all_instruments if
                                   instrument['name'].lower() == symbol.lower() and
                                   instrument['type'].lower() == inst_type.lower()]
                for instrument in same_instrument:
                    try:
                        con_id = instrument['tradableInstrumentId']
                        symbol = instrument['name']
                        tradelocker_symbol = instrument['name']
                        local_symbol = instrument['name']
                        inst_type = instrument['type']

                        # settings_for_sym = get_tradelocker_setting_for_user_by_local_symbol(local_symbol,
                        #                                                                     inst_type, None)
                        #
                        # if settings_for_sym is None:
                        #     settings_for_sym = get_tradelocker_setting_for_user_by_symbol(symbol,
                        #                                                                   inst_type, None)
                        #
                        # if settings_for_sym:
                        #     return {"data": f"Symbol Already Exists", "error": True}

                        order_type = 'market'
                        Exchange = instrument['tradingExchange']
                        routes = instrument['routes']
                        route = [str(route["id"]) for route in routes if route["type"] == 'TRADE'][0]
                        instrument_details = tl.get_instrument_details(con_id)
                        currency = instrument_details['quotingCurrency']
                        lot_size = instrument_details['lotSize']
                        min_tick = instrument_details['tickSize'][0]['tickSize']
                        strike_price_interval = instrument_details['strikePrice']
                        MaturityDate = instrument_details['lastTradeDate']
                        isin = instrument_details['isin']
                        quantity = 1
                        duplicate_position = False
                        cusip = None
                        settings = {
                            "LocalSymbol": local_symbol,
                            "SecurityType": inst_type,
                            "OrderType": order_type,
                            "Exchange": Exchange,
                            "Symbol": symbol,
                            "con_id": con_id,
                            "tradelocker_symbol": tradelocker_symbol,
                            "Currency": currency,
                            "LotSize": lot_size,
                            "MinTick": min_tick,
                            "strike_price_interval": strike_price_interval,
                            "MaturityDate": MaturityDate,
                            "isin": isin,
                            "quantity": quantity,
                            "duplicate_position": duplicate_position,
                            "cusip": cusip,
                            "route": route
                        }
                        return True, settings

                    except Exception as e:
                        logger.error(f"Error saving instrument: {traceback.format_exc()}")
                        continue
            except Exception as e:
                logger.error(f"Error in check_and_get_tradelocker_symbol: {traceback.format_exc()}")
                continue
    except Exception as e:
        logger.error(f"Error in check_and_get_tradelocker_symbol: {traceback.format_exc()}")
        return False, None
    return False, None


def new_save_tradelocker_setting(settings, user):
    try:



        new_symbol_settings = TradeLockerSetting()
        new_symbol_settings.random_id = user.random_id
        new_symbol_settings.local_symbol = settings.get('LocalSymbol').upper()
        new_symbol_settings.inst_type = settings.get('SecurityType').upper()
        new_symbol_settings.order_type = settings.get('OrderType').upper()
        new_symbol_settings.Exchange = settings.get('Exchange').upper()
        new_symbol_settings.symbol = settings.get('Symbol').upper()
        new_symbol_settings.con_id = settings.get('con_id')
        new_symbol_settings.tradelocker_symbol = settings.get('tradelocker_symbol').upper()
        new_symbol_settings.Currency = settings.get('Currency').upper()
        new_symbol_settings.lot_size = settings.get('LotSize')
        new_symbol_settings.min_tick = settings.get('MinTick')
        new_symbol_settings.strike_price_interval = settings.get('strike_price_interval')
        new_symbol_settings.isin = settings.get('isin')
        new_symbol_settings.quantity = settings.get('quantity')
        new_symbol_settings.route = settings.get('route')
        new_symbol_settings.server = settings.get('server', None)
        db_session.add(new_symbol_settings)
        db_session.commit()
        db_session.close()

        return {"data": f"Successfully Saved", "error": False}
    except Exception as e:
        logger.error(f"error in save setting {traceback.format_exc()}")
        return {"data" :f"Error in Setting Data {e}" ,"error" :True}