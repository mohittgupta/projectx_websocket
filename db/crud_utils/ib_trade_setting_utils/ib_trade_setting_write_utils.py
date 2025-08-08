import traceback

from sqlalchemy import and_

from config import logger
from db.crud_utils.ib_trade_setting_utils.ib_trade_settings_read_utils import get_ib_trade_setting_by_symbol_and_id, \
    get_ib_trade_setting_for_user_by_symbol, get_ib_trade_setting_for_user_by_local_symbol
from db.database import db_session
from db.models.ib_meta_data import IBMetaData
from db.models.ib_trade_setting import IBTradeSetting



def add_ib_initial_setting(random_id=None, chunk_size=1000):



    new_settings = []

    new_settings.append(
        IBTradeSetting(
            random_id=random_id,
            local_symbol='Common',
            inst_type='Common',
            order_type='Common',
            Exchange='Common',
            symbol='Common',
            con_id=0,
            ib_symbol='Common',
            Currency='Common',
            lot_size=1,
            min_tick=1,
            strike_price_interval=1,
            MaturityDate='23000101',
            isin='Common',
            quantity=1,
            duplicate_position=True,
            cusip='Common'
        )
    )

    # Bulk insert for the current chunk
    db_session.bulk_save_objects(new_settings)
    db_session.commit()



    db_session.close()


def save_ib_setting(settings,user):
    try:
        random_id = user.random_id
        new_symbol_settings = None

        settings_for_sym = get_ib_trade_setting_for_user_by_local_symbol(settings['LocalSymbol'], settings['SecurityType'], None)

        if settings_for_sym is None:
            settings_for_sym = get_ib_trade_setting_for_user_by_symbol(settings['Symbol'], settings['SecurityType'], None)




        if settings_for_sym is not None:

            new_symbol_settings.random_id = random_id
            new_symbol_settings.local_symbol = settings.get('Symbol', settings_for_sym.local_symbol).upper()
            new_symbol_settings.inst_type = settings.get('SecurityType', settings_for_sym.inst_type).upper()
            new_symbol_settings.order_type = settings.get('OrderType', settings_for_sym.order_type).upper()
            new_symbol_settings.Exchange = settings.get('Exchange', settings_for_sym.Exchange).upper()
            new_symbol_settings.symbol = settings.get('Symbol').upper()
            new_symbol_settings.con_id = settings.get('con_id', settings_for_sym.con_id)
            new_symbol_settings.ib_symbol = settings.get('LocalSymbol', settings_for_sym.ib_symbol).upper()
            new_symbol_settings.Currency = settings.get('Currency', settings_for_sym.Currency).upper()
            new_symbol_settings.lot_size = settings.get('LotSize', settings_for_sym.lot_size)
            new_symbol_settings.min_tick = settings.get('MinTick', settings_for_sym.min_tick)
            new_symbol_settings.strike_price_interval = settings.get('strike_price_interval', 5)
            new_symbol_settings.isin = settings.get('isin', settings_for_sym.isin)
            new_symbol_settings.quantity = settings.get('quantity', settings_for_sym.quantity)
            new_symbol_settings.cusip = settings.get('cusip', settings_for_sym.cusip)
            db_session.add(new_symbol_settings)
            db_session.commit()
            db_session.close()

        else:
            exchange = 'SMART'
            if settings.get('SecurityType').upper() in ['FUT', 'FOP']:
                exchange = 'CME'
            new_symbol_settings = IBTradeSetting()
            new_symbol_settings.random_id = random_id
            new_symbol_settings.local_symbol = settings.get('Symbol').upper()
            new_symbol_settings.inst_type = settings.get('SecurityType').upper()
            new_symbol_settings.order_type = settings.get('OrderType').upper()
            new_symbol_settings.symbol = settings.get('Symbol').upper()
            new_symbol_settings.ib_symbol = settings.get('LocalSymbol').upper()
            new_symbol_settings.Currency = settings.get('Currency', 'USD').upper()
            new_symbol_settings.lot_size = settings.get('LotSize')
            new_symbol_settings.min_tick = settings.get('MinTick')
            new_symbol_settings.isin = settings.get('isin', '')
            new_symbol_settings.Exchange = settings.get('Exchange', exchange).upper()
            new_symbol_settings.strike_price_interval = settings.get('strike_price_interval', 5)
            new_symbol_settings.quantity = settings.get('quantity', 1)
            new_symbol_settings.cusip = settings.get('cusip', '')

            db_session.add(new_symbol_settings)
            db_session.commit()
            db_session.close()

        return {"data": f"Successfully Saved", "error": False}
    except Exception as e:
        logger.error(f"error in save setting {traceback.format_exc()}")
        return {"data":f"Error in Setting Data {e}","error":True}


def add_ib_meta_data(data):
    try:
        ib_meta_data = IBMetaData()
        ib_meta_data.symbol = data[0]
        ib_meta_data.maturity_date = data[1]
        ib_meta_data.trading_class = data[2]
        ib_meta_data.inst_type = data[3]
        db_session.add(ib_meta_data)
        db_session.commit()


    except Exception as e:
        db_session.rollback()
    finally:
        db_session.close()


def convert_to_futures_code(contract_name):
    # Mapping of month abbreviations to futures codes
    month_codes = {
        "Jan": "F", "Feb": "G", "Mar": "H", "Apr": "J",
        "May": "K", "Jun": "M", "Jul": "N", "Aug": "Q",
        "Sep": "U", "Oct": "V", "Nov": "X", "Dec": "Z"
    }

    # Splitting the contract name
    parts = contract_name.split()

    # Extracting the ticker, month abbreviation, and year
    ticker = parts[0]  # e.g., "10Y"
    date_parts = parts[1].split("'")
    month_abbr = date_parts[0][:3]  # e.g., "Jan"
    year = date_parts[1][-1]  # Extracts the last digit of the year, e.g., '25' -> '5'

    # Get the corresponding month code
    month_code = month_codes.get(month_abbr, "")

    # Construct the futures contract code
    if month_code:
        return f"{ticker}{month_code}{year}"
    else:
        return "Invalid month abbreviation"

def ib_delete(symbol,user, inst_type):
    if symbol== 'COMMON':
        return {"data": f"Can Not Delete Common Setting", "error": True}
    settings_for_sym = get_ib_trade_setting_for_user_by_local_symbol(symbol, inst_type, user.random_id)
    if settings_for_sym is None:
        return {"data": f"Can't delete default setting", "error": True}
    else:
        db_session.delete(settings_for_sym)
        db_session.commit()
        db_session.close()
        return {"data": f"Successfully Delete", "error": False}


def save_ib_trade_settings(data):
    db_session.add(data)
    db_session.commit()
    db_session.close()

