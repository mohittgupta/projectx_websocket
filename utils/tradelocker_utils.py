import asyncio
import datetime
import json
import time
import requests
import traceback

import pandas as pd
from tradelocker import TLAPI
from tradelocker.utils import time_to_token_expiry
from config import logger
from db.crud_utils.multi_user_connection_utils.multi_user_read_utils import \
    get_multi_user_connections_by_connection_name, get_multi_user_engine_and_user_id
from db.crud_utils.trade_data_utils.trade_data_read_queries import get_by_date_alert_details
from db.crud_utils.trade_locker_position_utils.trade_locker_position_read_utils import \
    get_all_trade_locker_positions_by_side_and_instrument_id
from db.crud_utils.trade_locker_position_utils.trade_locker_position_write_utils import save_trade_locker_positions
from db.crud_utils.tradelocker_utils.tradeloacker_read_utils import get_instrument_data_using_con_id, \
    get_tradelocker_setting_for_user_by_local_symbol, get_tradelocker_setting_for_user_by_symbol
from db.crud_utils.tradelocker_utils.tradelocker_write_utils import save_tradelocker_setting
from db.database import db_session
from db.models.trade_locker_positions import trade_locker_positions
from utils.linetimer import timing_decorator
from utils.request_utils import send_request


# [{'id': 1222181, 'name': 'OSP#679342d7ca1b54c396cf1759#1#1', 'currency': 'USD', 'accNum': 1, 'accountBalance': 9926.94, 'status': 'ACTIVE'}]

async def get_trade_locker_all_accounts(user , connection_name):
    """
    Get all accounts from Trade Locker
    """
    all_accounts_dict = []
    user_multi_connection = get_multi_user_connections_by_connection_name(user.id, connection_name)
    if user_multi_connection:
        check_password = False
        tl = None
        if user_multi_connection.connection_access_token and user_multi_connection.connection_refresh_token:
            tl = TLAPI(
                environment=user_multi_connection.connection_environment,
                access_token=str(user_multi_connection.connection_access_token),
                refresh_token=str(user_multi_connection.connection_refresh_token),
            )

            all_accounts_df = tl.get_all_accounts()
            all_accounts_dict = all_accounts_df.to_dict(orient='records')
            return all_accounts_dict
    return []


async def place_tradelocker_trade(user, connection_name,
                                  route_id,
                                  instrument_id: int,
                                  quantity: float,
                                  side: str,
                                  order_type: str,
                                  price: float = None,
                                  sl_price: float = None,
                                  tp_price: float = None,
                                  sl_dollar: float = None,
                                  tp_dollar: float = None,
                                  reverse: bool = False,
                                  acc_id: str = None,
                                  ):
    """Places an order with absolute or offset SL & TP, handling position reversal or closure via API.

    Args:
        user: User instance
        connection_name (str): Name of the user connection
        instrument_id (int): Instrument ID for the trade
        quantity (float): Order quantity
        side (str): "buy" or "sell"
        order_type (str): "market" or "limit"
        price (float, optional): Required for limit orders
        sl_price (float, optional): Stop loss price (absolute)
        tp_price (float, optional): Take profit price (absolute)
        sl_dollar (float, optional): Stop loss in dollars (offset)
        tp_dollar (float, optional): Take profit in dollars (offset)
        reverse (bool): If True, close all opposite positions before placing a new order.

    Returns:
        tuple: (status_message, order_id, error_message)
    """
    try:
        start_time = time.time()
        # Normalize order type
        order_type = 'market' if order_type == 'MKT' else order_type
        order_type = 'limit' if order_type == 'LMT' else order_type
        if order_type not in ["market", "limit"]:
            raise ValueError("Invalid order_type. Use 'market' or 'limit'.")
        if order_type == "limit" and price is None:
            raise ValueError("Limit orders require a price.")
        current_time = time.time()
        logger.info(f"time taken : {current_time-start_time}")
        # Get instrument data (assumed function)
        instrument_data = get_instrument_data_using_con_id(instrument_id)
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        # Convert dollar-based SL/TP to price offsets
        tp_dollar = tp_dollar / instrument_data.min_tick if tp_dollar is not None else None
        sl_dollar = sl_dollar / instrument_data.min_tick if sl_dollar is not None else None

        stop_loss = sl_dollar if sl_dollar is not None else sl_price
        stop_loss_type = "offset" if sl_dollar is not None else "absolute" if sl_price is not None else None
        take_profit = tp_dollar if tp_dollar is not None else tp_price
        take_profit_type = "offset" if tp_dollar is not None else "absolute" if tp_price is not None else None
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        # Get user connection details
        user_multi_connection = get_multi_user_connections_by_connection_name(user.id, connection_name)
        if not user_multi_connection:
            return "No connection found", None, "Connection not found"
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        # Use TLAPI to manage tokens
        access_token = None
        refresh_token = None
        environment = user_multi_connection.connection_environment
        check_password = False

        if user_multi_connection.connection_access_token and user_multi_connection.connection_refresh_token:
            access_token = user_multi_connection.connection_access_token
        else:
            return "Authentication failed", None, "No valid access token"
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        # Assume accNum is stored in user_multi_connection or fetch it
        # acc_num = user_multi_connection.connection_account_number
        # acc_id = user_multi_connection.connection_account_id

        acc_num , acc_id = verify_and_get_account_number_by_account_id(user_multi_connection , acc_id)


        if acc_num is None:
            return "Account ID not valid", None, ""
        # Headers with accNum
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "accNum": acc_num  # Convert to string if needed
        }

        # Determine opposite side for position reversal
        opposite_side = "SELL" if side.upper() == "BUY" else "BUY"
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        # existing_positions = await get_all_tradelocker_postions(environment , acc_id , acc_num , access_token)
        existing_positions = get_all_trade_locker_positions_by_side_and_instrument_id(user.id , opposite_side, instrument_id)
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        closed = False
        new_quantity = float(quantity)
        for position in existing_positions:
            close_quantity = float(position.quantity) if reverse else min(float(position.quantity), new_quantity)
            position_id = position.position_id
            close_url = f"{environment}/backend-api/trade/positions/{position_id}"
            close_payload = {"quantity": str(close_quantity)}
            asyncio.create_task(send_request('DELETE', close_url, data=close_payload, params=None, headers=headers))
            position.active = False
            save_trade_locker_positions(position)
            closed = True
            if not reverse:
                new_quantity -= close_quantity
            if new_quantity <= 0:
                break
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        if not reverse and closed:
            return "Order placed ", None, ""

        # get route


        if route_id is None:
            return "Error Getting route id", None, ""
        # Prepare order payload
        order_url = f"{environment}/backend-api/trade/accounts/{acc_id}/orders"
        order_payload = {
            "routeId" : route_id,
            "tradableInstrumentId": str(instrument_id),
            "qty": str(quantity),
            "side": side.lower(),
            "type": order_type,
            "validity": "GTC" if order_type == "limit" else "IOC"
        }
        if order_type == "limit":
            order_payload["price"] = price
        if stop_loss is not None:
            order_payload["stopLoss"] = stop_loss
            order_payload["stopLossType"] = stop_loss_type
        if take_profit is not None:
            order_payload["takeProfit"] = take_profit
            order_payload["takeProfitType"] = take_profit_type

        # Place the order
        logger.info(f"Placing order for {instrument_id} with quantity {quantity} and side {side}")
        response = await send_request('POST', order_url, data=order_payload, params=None, headers=headers)
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        if response.status_code == 200:
            logger.info(f"Order placed successfully: {response.json()}")
            if response.json()['s'] != 'ok':
                return response.json()['errmsg'], None, response.json()['errmsg']
            order_id = response.json()['d'].get("orderId")  # Adjust based on actual response
            return "Order placed", order_id, ""
        else:
            if response.status_code == 401:
                return "Token expired", None, "Authentication token expired"
            raise Exception(f"Failed to place order: {response.status_code} - {response.text}")

    except Exception as e:
        logger.info(f"Error in place_tradelocker_trade: {traceback.format_exc()}")
        return str(e), None, str(e)

async def close_trade_locker_position(user, connection_name, instrument_id: int, acc_id: str = None):
    """Closes all positions for a given instrument ID.

    Args:
        user: User instance
        connection_name (str): Name of the user connection
        instrument_id (int): Instrument ID whose positions need to be closed

    Returns:
        bool: True if successful, False otherwise
    """
    user_multi_connection = get_multi_user_connections_by_connection_name(user.id, connection_name)
    if not user_multi_connection:
        return False

    environment = user_multi_connection.connection_environment
    check_password = False
    access_token = None
    if user_multi_connection.connection_access_token and user_multi_connection.connection_refresh_token:
        access_token = user_multi_connection.connection_access_token
        refresh_token = user_multi_connection.connection_refresh_token

    # acc_num = user_multi_connection.connection_account_number
    # acc_id = user_multi_connection.connection_account_id

    acc_num , acc_id = verify_and_get_account_number_by_account_id(user_multi_connection , acc_id)
    # Headers with accNum
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "accNum": acc_num  # Convert to string if needed
    }

    order_url = f"{environment}/backend-api/trade/accounts/{acc_id}/positions"
    order_payload = {"tradableInstrumentId" : instrument_id}

    # Place the order
    logger.info(f"Closed all positions order for {instrument_id}")
    response = await send_request('DELETE', order_url, data=order_payload, params=None, headers=headers)
    response_json = response.json()

    response_status: str = response_json['s']
    return response_status == "ok"

def fetch_and_save_all_instruments(user , connection_name):
    try :
        logger.info(f"Fetching all instruments for user {user.id}")
        user_multi_connection = get_multi_user_connections_by_connection_name(user.id, connection_name)
        if user_multi_connection:

            tl = TLAPI(
                environment=user_multi_connection.connection_environment,
                username=user_multi_connection.connection_username,
                password=user_multi_connection.connection_password,
                server=user_multi_connection.connection_server
            )
            access_token = tl.get_access_token()
            refresh_token = tl.get_refresh_token()
            all_accounts_df = tl.get_all_accounts()
            all_accounts_dict = all_accounts_df.to_dict(orient='records')
            all_accounts_list = []
            account_to_acc_num = {}
            for accounts in all_accounts_dict:
                all_accounts_list.append(str(accounts['id']))
                account_to_acc_num[accounts['id']] = accounts['accNum']
            specific_account_id = all_accounts_list
            user_multi_connection.connection_access_token = access_token
            user_multi_connection.connection_refresh_token = refresh_token
            user_multi_connection.connection_account_number = json.dumps(account_to_acc_num)
            user_multi_connection.connection_account_id = json.dumps(all_accounts_list)
            server = user_multi_connection.connection_server
            db_session.add(user_multi_connection)
            db_session.commit()
            db_session.close()
            if tl is None:
                return None
            all_instruments_df = tl.get_all_instruments()
            all_instruments = all_instruments_df.to_dict(orient='records')
            for instrument in all_instruments:
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
                    route = [ str(route["id"]) for route in routes if route["type"] == 'TRADE' ][0]
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
                        "route" : route,
                        'server' : server,
                        }

                    save_tradelocker_setting(settings, server)
                except Exception as e:
                    logger.error(f"Error saving instrument: {traceback.format_exc()}")
                    continue

    except Exception as e:
        print(traceback.format_exc())
        logger.error(f"Error in fetch_and_save_all_instruments: {traceback.format_exc()}")
        return None

def get_all_oders_from_entry_order(user, connection_name, entry_order_id):
    user_multi_connection = get_multi_user_connections_by_connection_name(user.id, connection_name)

    stop_order_id = None
    limit_order_id = None
    if user_multi_connection:
        check_password = False
        tl = None
        if user_multi_connection.connection_access_token and user_multi_connection.connection_refresh_token:
            tl = TLAPI(
                environment=user_multi_connection.connection_environment,
                access_token=str(user_multi_connection.connection_access_token),
                refresh_token=str(user_multi_connection.connection_refresh_token),
            )

            ORDERS = tl.get_all_orders()

            allorder = ORDERS.to_dict(orient='records')

            current_order_pos_id = tl.get_position_id_from_order_id(order_id=int(entry_order_id))

            asyncio.create_task(get_and_save_position_details(current_order_pos_id, user, connection_name))


            # get all orders from the order history that has given position id and the order id that matches with the current order id is entry order , one with stop is stop los and limit is take profit
            for order in allorder:
                if order['positionId'] == current_order_pos_id:
                    if order['id'] == entry_order_id:
                        entry_order_id = order['id']
                    if order['type'] == 'stop':
                        stop_order_id = order['id']
                    if order['type'] == 'limit':
                        limit_order_id = order['id']


    return entry_order_id , stop_order_id , limit_order_id

def get_all_tradelocker_orders(user, connection_name):
    try:
        user_multi_connection = get_multi_user_connections_by_connection_name(user.id, connection_name)

        if user_multi_connection:
            if user_multi_connection.connection_access_token and user_multi_connection.connection_refresh_token:
                tl = TLAPI(
                    environment=user_multi_connection.connection_environment,
                    access_token=str(user_multi_connection.connection_access_token),
                    refresh_token=str(user_multi_connection.connection_refresh_token),
                )

                ORDERS = tl.get_all_orders(lookback_period= '1D',history=True)

                allorder = ORDERS.to_dict(orient='records')

                return allorder
    except Exception as e:
        logger.info(f"error {str(e)}")
        return []

def get_tradelocker_rder_date(timestamp):
    order_date = datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return order_date


def get_alerts_datafor_user(user,from_date,to_date, engine):
    all_orders = []
    try:
        data = get_by_date_alert_details(user,datetime.datetime.strptime( from_date,'%Y-%m-%d'),datetime.datetime.strptime( to_date,'%Y-%m-%d') + datetime.timedelta(days=1), engine)
        df = pd.DataFrame([vars(obj) for obj in data])
        if (len(df) > 0):
            df = df.drop(columns=['_sa_instance_state'])
            df_sorted = df.sort_values(by='row_id', ascending=False)
            df_one_column = df_sorted[['entry_id','lmt_id','stp_id']]
            all_orders = df_one_column['entry_id'].tolist() + df_one_column['lmt_id'].tolist() + df_one_column['stp_id'].tolist()
            return all_orders
    except Exception as e:
        logger.error(f"error in alert data {traceback.format_exc()}")
    return all_orders

async def save_token_for_tradelocker_user(user_multi_connection):
    try:

        if user_multi_connection.connection_access_token is None:
            return True

        if user_multi_connection.connection_access_token:
            if time_to_token_expiry(user_multi_connection.connection_access_token) > 200 :
                return True

        tl = TLAPI(
            environment=user_multi_connection.connection_environment,
            username=user_multi_connection.connection_username,
            password=user_multi_connection.connection_password,
            server=user_multi_connection.connection_server
        )
        access_token = tl.get_access_token()
        refresh_token = tl.get_refresh_token()
        all_accounts_df = tl.get_all_accounts()
        all_accounts_dict = all_accounts_df.to_dict(orient='records')
        all_accounts_list = []
        account_to_acc_num = {}
        for accounts in all_accounts_dict:
            all_accounts_list.append(str(accounts['id']))
            account_to_acc_num[accounts['id']] = accounts['accNum']
        specific_account_id = all_accounts_list
        user_multi_connection.connection_access_token = access_token
        user_multi_connection.connection_refresh_token = refresh_token
        user_multi_connection.connection_account_number = json.dumps(account_to_acc_num)
        user_multi_connection.connection_account_id = json.dumps(all_accounts_list)
        db_session.add(user_multi_connection)
        db_session.commit()
        db_session.close()
    except Exception as e:
        logger.infor(f"Error while save access token for user {user_multi_connection.user_id}")
    finally:
        return True


def get_instrument_route(environment , account_id , account_number , access_token , instrument_id):
    all_instrument_url = order_url = f"{environment}/backend-api/trade/accounts/{account_id}/instruments"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "accNum": account_number  # Convert to string if needed
    }


    response = requests.get(all_instrument_url, headers=headers)
    logger.info(f"Response for all instruments {response.json()}")
    resp_json = response.json()['d']['instruments']
    desired_route = None
    for resp in resp_json :
        if resp['tradableInstrumentId'] == instrument_id:
            routes = resp['routes']
            matching_routes: list[str] = [
                str(route["id"]) for route in routes if route["type"] == 'TRADE'
            ]
            desired_route = matching_routes[0]

    return desired_route



async def get_all_tradelocker_postions(environment, acc_id, acc_num, access_token):
    try:
        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "accNum": acc_num  # Convert to string if needed
        }
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")

        default_columns = ['id', 'tradableInstrumentId', 'routeId', 'side', 'qty', 'avgPrice',
                           'stopLossId', 'takeProfitId', 'openDate', 'unrealizedPl', 'strategyId']
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        positions_url = f"{environment}/backend-api/trade/accounts/{acc_id}/positions"
        positions_response = await send_request('GET', positions_url, headers=headers)
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        if positions_response.status_code != 200:
            raise Exception(f"Failed to fetch positions: {positions_response.text}")
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        existing_positions = positions_response.json().get('d', {}).get('positions', [])
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        # If positions exist and column length doesn't match, fetch config
        if existing_positions and len(default_columns) != len(existing_positions[0]):
            config_url = f"{environment}/backend-api/trade/config"
            config_response = await send_request('GET', config_url, headers=headers)

            if config_response.status_code == 200:
                config_data = config_response.json().get('d', {}).get('positionsConfig', {}).get('columns', [])
                if config_data:
                    default_columns = [col["id"] for col in config_data]
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        # Ensure each position dictionary has all expected columns
        new_psotions = []
        for position in existing_positions:
            new_position = dict(zip(default_columns, position))
            new_psotions.append(new_position)
        current_time = time.time()
        logger.info(f"time taken : {current_time - start_time}")
        return new_psotions

    except Exception as e:
        logger.error(f"Error fetching positions: {str(e)}")
        return []


async def get_and_save_position_details(position_id , user, connection_name):
    user_multi_connection = get_multi_user_connections_by_connection_name(user.id, connection_name)

    stop_order_id = None
    limit_order_id = None
    if user_multi_connection:
        check_password = False
        tl = None
        if user_multi_connection.connection_access_token and user_multi_connection.connection_refresh_token:
            tl = TLAPI(
                environment=user_multi_connection.connection_environment,
                access_token=str(user_multi_connection.connection_access_token),
                refresh_token=str(user_multi_connection.connection_refresh_token),
            )
        all_positions = tl.get_all_positions()
        all_positions = all_positions.to_dict(orient='records')
        for position in all_positions:
            if position['id'] == position_id:
                trade_locker_position = trade_locker_positions()
                trade_locker_position.user_id = user.id
                trade_locker_position.position_id = position_id
                trade_locker_position.side = position['side']
                trade_locker_position.tradable_instrument_id = position['tradableInstrumentId']
                trade_locker_position.quantity = position['qty']
                trade_locker_position.active = True
                save_trade_locker_positions(trade_locker_position)

    return True

def verify_and_get_account_number_by_account_id(user_connection , account_id):
    user_account_ids = json.loads(user_connection.connection_account_id)
    user_account_numbers = json.loads(user_connection.connection_account_number)
    account_number = None
    if account_id not in user_account_ids:
        return None , None
    else:

        account_number = user_account_numbers[account_id]
        return str(account_number) , str(account_id)

