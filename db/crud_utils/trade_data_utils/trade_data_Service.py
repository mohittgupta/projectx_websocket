import datetime

from db.crud_utils.trade_data_utils.trade_data_write_queries import save_trade_data
from db.models.trade_data import trade_data


def save_trade_data_msg(user_req,token,status,user,order_type="MKT" , platform='RITHMIC'):
    new_trade_data = trade_data()
    new_trade_data.user_id = token
    new_trade_data.symbol = user_req['symbol']
    new_trade_data.local_symbol = user_req['symbol']
    new_trade_data.alert_data = str(user_req)
    new_trade_data.server_date_time = datetime.datetime.now()
    new_trade_data.tradeDate = datetime.datetime.now().date()
    new_trade_data.alert_status = f"{status}"
    new_trade_data.demo = user.demo
    new_trade_data.trade_time = str(user_req['date'])
    side = user_req['data'].split('-')[0].upper()
    new_trade_data.buy_sell = side
    new_trade_data.order_type = order_type
    new_trade_data.platform = platform
    save_trade_data(new_trade_data)


def save_trade_data_msg_for_watch(symbol,side,user_req,token,status,user,order_type="MKT"):
    new_trade_data = trade_data()
    new_trade_data.user_id = token
    new_trade_data.symbol = symbol
    new_trade_data.local_symbol = symbol
    new_trade_data.alert_data = str(user_req)
    new_trade_data.server_date_time = datetime.datetime.now()
    new_trade_data.tradeDate = datetime.datetime.now().date()
    new_trade_data.alert_status = f"{status}"
    new_trade_data.demo = user.demo
    new_trade_data.trade_time = str(datetime.datetime.now())
    new_trade_data.buy_sell = side
    new_trade_data.order_type = order_type
    save_trade_data(new_trade_data)
