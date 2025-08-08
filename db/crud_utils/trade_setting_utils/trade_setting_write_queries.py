import traceback

from business_logic.common_utils import get_tick_lot
from business_logic.rollover import create_new_rollover_setting

from db.crud_utils.login_central_utils.login_central_read_queries import get_by_random_key, get_by_user_name
from db.models.trade_setting import trade_setting
from db.crud_utils.trade_setting_utils.trade_setting_read_queries import *
from db.database import db_session
from config import default_setting, logger, default_symbol_with_ticks, admin_url



def save_trade_setting_db(entity):
    db_session.add(entity)
    db_session.commit()
    db_session.close()

def delete(symbol,user):
    if symbol== 'COMMON':
        return {"data": f"Can Not Delete Common Setting", "error": True}
    settings_for_sym = get_setting_for_use_by_rithmic_symbol_and_user(symbol,user.random_id)
    if settings_for_sym is None:
        return {"data": f"Can't delete default setting", "error": True}
    else:
        db_session.delete(settings_for_sym)
        db_session.commit()
        db_session.close()
        return {"data": f"Successfully Delete", "error": False}



def save_setting(settings,user):
    try:
        random_id = user.random_id
        new_symbol_settings = None
        settings_for_sym = get_setting_by_symbol_and_id(settings['Symbol'],random_id)
        if settings_for_sym is None:
            new_symbol_settings = trade_setting()
        else:
            new_symbol_settings = settings_for_sym
        new_symbol_settings.random_id = random_id
        new_symbol_settings.symbol = settings['Symbol'].upper()
        new_symbol_settings.local_symbol = settings['LocalSymbol'].upper()

        new_symbol_settings.lot_size = float(settings['LotSize']) if ('LotSize' in settings) and settings['LotSize'] != "" else 0
        new_symbol_settings.min_tick = float(settings['MinTick']) if ('MinTick' in settings) and settings['MinTick'] != "" else 0

        new_symbol_settings.Exchange = settings['Exchange'] if ('Exchange' in settings)  else ""

        new_symbol_settings.manualchange = settings['ManualChange'] if ('ManualChange' in settings) else False

        if new_symbol_settings.lot_size == 0 or new_symbol_settings.min_tick == 0:
            data = get_tick_lot(settings['Symbol'])
            if new_symbol_settings.lot_size == 0:
                logger.info(f"adding lot size user didn't enter lot {settings['Symbol']} {data['lot']}")
                new_symbol_settings.lot_size = data['lot']
            if new_symbol_settings.min_tick == 0:
                logger.info(f"adding lot size user didn't enter ticks {settings['Symbol']} {data['ticks']}")
                new_symbol_settings.min_tick = data['ticks']


        new_symbol_settings.order_type = settings['OrderType'] if ('OrderType' in settings) and settings['OrderType'] != "" else 'MKT'
        new_symbol_settings.quantity = int(settings['Quantity'])
        new_symbol_settings.inst_type = settings['SecurityType']
        new_symbol_settings.stop_loss = settings['StopLoss']
        new_symbol_settings.take_profit = settings['TakeProfit']
        new_symbol_settings.eEntryOffset = settings['EntryOffset']
        new_symbol_settings.percentage = settings['QuantityType']
        if 'EntryOffsetInPercentage' in settings:
            new_symbol_settings.EntryOffsetInPercentage = settings['EntryOffsetInPercentage']
        else:
            new_symbol_settings.EntryOffsetInPercentage = False
        if 'TakeProfitPercentage' in settings:
            new_symbol_settings.take_profit_percentage = settings['TakeProfitPercentage']
        else:
            new_symbol_settings.take_profit_percentage = False
        if 'StopLossPercentage' in settings:
            new_symbol_settings.stop_loss_percentage = settings['StopLossPercentage']
        else:
            new_symbol_settings.stop_loss_percentage = False

        new_symbol_settings.moc_order = False
        new_symbol_settings.timezone = default_setting.get("timezone")
        new_symbol_settings.date_validation = False
        new_symbol_settings.trailing_stop = False
        new_symbol_settings.account = ""
        new_symbol_settings.trailing_stop_percentage = 0
        # new_symbol_settings.min_tick = 0
        new_symbol_settings.position_trade = False
        new_symbol_settings.sttpexitTime = 0
        new_symbol_settings.reverse_trade = False
        new_symbol_settings.duplicate_position = True
        new_symbol_settings.rth = False
        new_symbol_settings.maximumOrder = -1
        db_session.add(new_symbol_settings)
        logger.info(f'{random_id} Saving settings for symbol {new_symbol_settings}   ')
        db_session.commit()
        db_session.close()
        return {"data": f"Successfully Saved", "error": False}
    except Exception as e:
        logger.error(f"error in save setting {traceback.format_exc()}")
        return {"data":f"Error in Setting Data {e}","error":True}


async def add_initial_common_settings(random_key=None):
    """Add settings for the "COMMON" symbol.
    COMMON here implies settings that are common to all symbols.
    """
    common_settings = get_setting_by_symbol_and_id('COMMON',random_key)
    if common_settings is None:
        new_symbol_settings = trade_setting()
        new_symbol_settings.random_id = random_key
        new_symbol_settings.symbol = 'COMMON'
        new_symbol_settings.order_type = 'MKT'
        new_symbol_settings.quantity = 1
        new_symbol_settings.min_tick = 0.01
        new_symbol_settings.lot_size = 100
        new_symbol_settings.local_symbol = 'All'
        new_symbol_settings.inst_type = 'STK'
        new_symbol_settings.stop_loss = 0
        new_symbol_settings.take_profit = 0
        new_symbol_settings.eEntryOffset = 0
        new_symbol_settings.percentage = 'quantity'
        new_symbol_settings.EntryOffsetInPercentage = False
        new_symbol_settings.take_profit_percentage = False
        new_symbol_settings.stop_loss_percentage = False

        new_symbol_settings.moc_order = False
        new_symbol_settings.timezone = default_setting.get("timezone")
        new_symbol_settings.date_validation = False
        new_symbol_settings.trailing_stop = False
        new_symbol_settings.account = ""
        new_symbol_settings.trailing_stop_percentage = 0
        new_symbol_settings.position_trade = False
        new_symbol_settings.sttpexitTime = 0
        new_symbol_settings.duplicate_position = True
        new_symbol_settings.reverse_trade = False
        new_symbol_settings.rth=False
        new_symbol_settings.maximumOrder=-1
        db_session.add(new_symbol_settings)
        db_session.commit()
        db_session.close()
        await add_symbol_setting(random_key)




async def add_symbol_setting(random_key):
    user = await get_by_user_name(admin_url[0])
    default_user = await get_by_random_key(random_key)
    await create_new_rollover_setting(user,default_user)
    # data = [default_symbol_with_ticks]
    # for d in data:
    #     new_symbol_settings = trade_setting()
    #     new_symbol_settings.random_id = random_key
    #     new_symbol_settings.symbol = d['Symbol']
    #     new_symbol_settings.order_type = 'MKT'
    #     new_symbol_settings.quantity = 1
    #     new_symbol_settings.min_tick =d['MinTick']
    #     new_symbol_settings.lot_size = d['LotSize']
    #     new_symbol_settings.local_symbol = d['LocalSymbol']
    #     new_symbol_settings.inst_type = 'FUT'
    #     new_symbol_settings.stop_loss = 1
    #     new_symbol_settings.take_profit = 1
    #     new_symbol_settings.eEntryOffset = 1
    #     new_symbol_settings.percentage = 'quantity'
    #     new_symbol_settings.EntryOffsetInPercentage = True
    #     new_symbol_settings.take_profit_percentage = True
    #     new_symbol_settings.stop_loss_percentage = True
    #
    #     new_symbol_settings.moc_order = False
    #     new_symbol_settings.timezone = default_setting.get("timezone")
    #     new_symbol_settings.date_validation = False
    #     new_symbol_settings.trailing_stop = False
    #     new_symbol_settings.account = ""
    #     new_symbol_settings.trailing_stop_percentage = 0
    #     new_symbol_settings.position_trade = False
    #     new_symbol_settings.sttpexitTime = 0
    #     new_symbol_settings.duplicate_position = True
    #     new_symbol_settings.reverse_trade = False
    #     new_symbol_settings.rth = False
    #     new_symbol_settings.maximumOrder = -1
    #     db_session.add(new_symbol_settings)
    #     db_session.commit()
    #     db_session.close()
