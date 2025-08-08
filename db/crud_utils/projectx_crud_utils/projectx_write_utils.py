import traceback

from config import logger, projectx_api_endpoints
from db.crud_utils.ib_trade_setting_utils.ib_trade_settings_read_utils import \
    get_ib_trade_setting_for_user_by_local_symbol
from db.crud_utils.multi_user_connection_utils.multi_user_read_utils import get_multi_user_engine_and_user_id
from db.crud_utils.projectx_crud_utils.projectx_read_utils import get_projectx_settings_for_user_by_local_symbol, \
    get_projectx_settings_for_user_by_symbol, get_projectx_settings_for_user_by_local_symbol_x
from db.crud_utils.tradelocker_utils.tradelocker_write_utils import new_save_tradelocker_setting
from db.database import db_session
from db.models.ib_trade_setting import IBTradeSetting
from utils.projectX_utils import search_contracts


async def save_projectx_setting_by_random_id(settings ,user):
    try:
        random_id = user.random_id
        new_symbol_settings = None
        check_server = False
        status = False
        resp = None
        settings_for_sym = get_projectx_settings_for_user_by_local_symbol(settings['LocalSymbol'], settings['SecurityType'], None)

        if settings_for_sym is None:
            settings_for_sym = get_projectx_settings_for_user_by_symbol(settings['Symbol'], settings['SecurityType'], None)

        if settings_for_sym is None:
            check_server = True
            status, resp = await check_and_get_projectx_symbol(user, settings['Symbol'], settings['LocalSymbol'])



        if settings_for_sym is None and check_server is True and status is False:
            return {"data": f"Symbol Not Found in ProjectX Server", "error": True}

        elif settings_for_sym is not None:
            new_symbol_settings = IBTradeSetting()
            new_symbol = settings_for_sym.symbol
            new_symbol_settings.random_id = random_id
            new_symbol_settings.local_symbol = settings.get('LocalSymbol', settings_for_sym.local_symbol).upper()
            new_symbol_settings.inst_type = settings.get('SecurityType', settings_for_sym.inst_type).upper()
            new_symbol_settings.order_type = settings.get('OrderType', settings_for_sym.order_type).upper()
            new_symbol_settings.Exchange = settings.get('Exchange', settings_for_sym.Exchange).upper()
            new_symbol_settings.symbol = settings.get('Symbol', new_symbol).upper()
            new_symbol_settings.con_id = settings.get('con_id', settings_for_sym.con_id)
            new_symbol_settings.ib_symbol = settings_for_sym.ib_symbol
            new_symbol_settings.Currency = settings.get('Currency', settings_for_sym.Currency).upper()
            new_symbol_settings.lot_size = settings.get('LotSize', settings_for_sym.lot_size)
            new_symbol_settings.min_tick = settings.get('MinTick', settings_for_sym.min_tick)
            new_symbol_settings.strike_price_interval = settings.get('strike_price_interval', settings_for_sym.strike_price_interval)
            new_symbol_settings.isin = settings.get('isin', settings_for_sym.isin)
            new_symbol_settings.quantity = settings.get('quantity', settings_for_sym.quantity)
            new_symbol_settings.cusip = settings.get('cusip', settings_for_sym.cusip)
            new_symbol_settings.projectx_id = settings_for_sym.projectx_id
            db_session.add(new_symbol_settings)
            db_session.commit()
            db_session.close()

            return {"data": f"Successfully Saved", "error": False}
        elif settings_for_sym is None and check_server is True and status is True:
            new_symbol_settings = IBTradeSetting()
            new_symbol_settings.random_id = random_id
            new_symbol_settings.local_symbol = settings.get('LocalSymbol').upper()
            new_symbol_settings.inst_type = settings.get('SecurityType').upper()
            new_symbol_settings.order_type = settings.get('OrderType').upper()
            new_symbol_settings.symbol = settings.get('Symbol').upper()
            new_symbol_settings.Currency = settings.get('Currency', 'USD').upper()
            new_symbol_settings.lot_size = settings.get('LotSize')
            new_symbol_settings.min_tick = settings.get('MinTick')
            new_symbol_settings.isin = settings.get('isin', '')
            new_symbol_settings.quantity = settings.get('quantity', 1)
            new_symbol_settings.cusip = settings.get('cusip', '')
            new_symbol_settings.projectx_id = resp.upper()
            db_session.add(new_symbol_settings)
            db_session.commit()
            db_session.close()
            return {"data": f"Successfully Saved", "error": False}
    except Exception as e:
        logger.error(f"error in save setting {traceback.format_exc()}")
        return {"data" :f"Error in Setting Data {e}" ,"error" :True}


async def check_and_get_projectx_symbol(user, symbol, porjectx_id):
    try:
        all_connections = get_multi_user_engine_and_user_id(engine='PROJECTX', user_id=user.id)
        if not all_connections:
            return False, None
        for connection in all_connections:
            server = connection.connection_server
            token = connection.connection_access_token
            BASE_URL = projectx_api_endpoints.get(connection.connection_server)
            contracts = await search_contracts(base_url=BASE_URL, token=token, search_text=symbol, live=False)
            for con in contracts:
                if symbol.upper() == con['name']:
                    return True, con['id']
                elif porjectx_id.upper() == con['name']:
                    return True, con['id']

            return  False , None

    except Exception as e:
        logger.error(f"Error in check_and_get_tradelocker_symbol: {traceback.format_exc()}")
        return False, None
    return False, None


def projectx_delete(symbol,user, inst_type):
    if symbol== 'COMMON':
        return {"data": f"Can Not Delete Common Setting", "error": True}
    settings_for_sym = get_projectx_settings_for_user_by_local_symbol_x(symbol, inst_type, user.random_id)
    if settings_for_sym is None:
        return {"data": f"Can't delete default setting", "error": True}
    else:
        db_session.delete(settings_for_sym)
        db_session.commit()
        db_session.close()
        return {"data": f"Successfully Delete", "error": False}