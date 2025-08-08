import datetime
import time
import traceback
import requests
import json
from typing import Dict, Any, Optional, List
from config import logger, projectx_api_endpoints
from db.crud_utils.ib_trade_setting_utils.ib_trade_setting_write_utils import save_ib_trade_settings
from db.crud_utils.ib_trade_setting_utils.ib_trade_settings_read_utils import get_ib_symbol_by_inst_type_list, \
    get_ib_trade_setting_for_user_by_local
from db.crud_utils.multi_user_connection_utils.multi_user_connection_write_utils import update_multi_user_connection
from db.crud_utils.multi_user_connection_utils.multi_user_read_utils import \
    get_multi_user_connections_by_connection_name, get_multi_user_by_engine
from utils.request_utils import send_request


# Helper function to make API requests
async def make_request(
        BASE_URL: str,
        endpoint: str,
        method: str = "POST",
        body: Optional[Dict] = None,
        include_token: bool = False,
        SESSION_TOKEN: Optional[str] = None
) -> Dict:
    """
    Generic function to make HTTP requests to the API.

    Args:
        BASE_URL: Base URL for the API
        endpoint: API endpoint (e.g., '/Auth/loginKey')
        method: HTTP method (default: 'POST')
        body: Request payload as a dictionary
        include_token: Whether to include the session token in the Authorization header
        SESSION_TOKEN: Session token for authentication

    Returns:
        Parsed JSON response

    Raises:
        Exception: If the request fails or the response indicates an error
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Accept": "text/plain",
        "Content-Type": "application/json",
    }

    if include_token and SESSION_TOKEN:
        headers["Authorization"] = f"Bearer {SESSION_TOKEN}"

    try:
        response = await send_request(method, url, data=body, params=None, headers=headers)
        logger.info(f'{method} {url} - Status Code: {response.status_code}, Response: {response.text}')
        response_data = response.json()
        return response_data
    except Exception as e:
        logger.info(f"Error in {method} {url}: {str(e)}")
        return {"success": False, "error": str(e)}


# Authenticate with API key to obtain session token
async def projectx_authenticate(base_url: str, user_name: str, api_key: str) -> Dict:
    """
    Authenticate with the API to obtain a session token.

    Args:
        base_url: Base URL for the API
        user_name: Username for authentication
        api_key: API key for authentication

    Returns:
        Response containing the session token
    """
    endpoint = "/Auth/loginKey"
    body = {
        "userName": user_name,
        "apiKey": api_key,
    }
    response = await make_request(BASE_URL=base_url, endpoint=endpoint, body=body)
    return response


# Validate session token and refresh if expired
async def validate_token(base_url: str, token: str) -> Dict:
    """
    Validate the current session token and refresh if expired.

    Args:
        base_url: Base URL for the API
        token: Authentication token

    Returns:
        Response containing validation status and optionally a new token
    """
    endpoint = "/Auth/validate"
    response = await make_request(BASE_URL=base_url, endpoint=endpoint, include_token=True, SESSION_TOKEN=token)
    return response


# Search for accounts
async def search_accounts(base_url: str, token: str, only_active_accounts: bool = False) -> List[Dict]:
    """
    Search for accounts.

    Args:
        base_url: Base URL for the API
        token: Authentication token
        only_active_accounts: Filter only active accounts

    Returns:
        List of account dictionaries
    """
    endpoint = "/Account/search"
    body = {
        "onlyActiveAccounts": only_active_accounts,
    }
    response = await make_request(BASE_URL=base_url, endpoint=endpoint, body=body, include_token=True, SESSION_TOKEN=token)
    return response.get("accounts", [])


# Search for contracts
async def search_contracts(base_url: str, token: str, search_text: str = "", live: bool = False) -> List[Dict]:
    """
    Search for contracts.

    Args:
        base_url: Base URL for the API
        token: Authentication token
        search_text: Contract name to search for
        live: Whether to search using live data subscription

    Returns:
        List of contract dictionaries
    """
    endpoint = "/Contract/search"
    body = {
        "searchText": search_text,
        "live": live,
    }
    response = await make_request(BASE_URL=base_url, endpoint=endpoint, body=body, include_token=True, SESSION_TOKEN=token)
    return response.get("contracts", [])


# Search for open orders
async def search_open_orders(base_url: str, token: str, account_id: int) -> List[Dict]:
    """
    Search for open orders for a specific account.

    Args:
        base_url: Base URL for the API
        token: Authentication token
        account_id: ID of the account

    Returns:
        List of open order dictionaries
    """
    endpoint = "/Order/searchOpen"
    body = {
        "accountId": account_id,
    }
    response = await make_request(BASE_URL=base_url, endpoint=endpoint, body=body, include_token=True, SESSION_TOKEN=token)
    return response.get("orders", [])


# Search for all orders
async def search_all_orders(base_url: str, token: str, account_id: int, start_timestamp: str, end_timestamp: str) -> List[Dict]:
    """
    Search for all orders for a specific account within a time range.

    Args:
        base_url: Base URL for the API
        token: Authentication token
        account_id: ID of the account
        start_timestamp: Start timestamp for the order search (ISO 8601 format)
        end_timestamp: End timestamp for the order search (ISO 8601 format)

    Returns:
        List of order dictionaries
    """
    endpoint = "/Order/search"
    body = {
        "accountId": account_id,
        "startTimestamp": start_timestamp,
        "endTimestamp": end_timestamp
    }
    response = await make_request(BASE_URL=base_url, endpoint=endpoint, body=body, include_token=True, SESSION_TOKEN=token)
    return response.get("orders", [])


# Place an order
async def place_order(
        base_url: str,
        token: str,
        account_id: int,
        contract_id: str,
        order_type: int,
        side: int,
        size: int,
        **options: Any
) -> int:
    """
    Place an order.

    Args:
        base_url: Base URL for the API
        token: Authentication token
        account_id: ID of the account
        contract_id: ID of the contract
        order_type: Order type (1=Limit, 2=Market, 4=Stop, 5=TrailingStop, 6=JoinBid, 7=JoinAsk)
        side: Order side (0=Buy, 1=Sell)
        size: Order size
        **options: Optional parameters (limitPrice, stopPrice, trailPrice, customTag, linkedOrderId)

    Returns:
        Order ID
    """
    endpoint = "/Order/place"
    body = {
        "accountId": account_id,
        "contractId": contract_id,
        "type": order_type,
        "side": side,
        "size": size,
    }
    response = await make_request(BASE_URL=base_url, endpoint=endpoint, body=body, include_token=True, SESSION_TOKEN=token)
    return response.get("orderId", 0)


# Cancel an order
async def cancel_order(base_url: str, token: str, account_id: int, order_id: int) -> Dict:
    """
    Cancel an order.

    Args:
        base_url: Base URL for the API
        token: Authentication token
        account_id: ID of the account
        order_id: ID of the order to cancel

    Returns:
        Response indicating success or failure
    """
    endpoint = "/Order/cancel"
    body = {
        "accountId": account_id,
        "orderId": order_id,
    }
    response = await make_request(BASE_URL=base_url, endpoint=endpoint, body=body, include_token=True, SESSION_TOKEN=token)
    return response


# Search for open positions
async def search_open_positions(base_url: str, token: str, account_id: int) -> List[Dict]:
    """
    Search for open positions for a specific account.

    Args:
        base_url: Base URL for the API
        token: Authentication token
        account_id: ID of the account

    Returns:
        List of open position dictionaries
    """
    endpoint = "/Position/searchOpen"
    body = {
        "accountId": account_id,
    }
    response = await make_request(BASE_URL=base_url, endpoint=endpoint, body=body, include_token=True, SESSION_TOKEN=token)
    return response.get("positions", [])


# Close a position
async def close_position(base_url: str, token: str, account_id: int, contract_id: str) -> Dict:
    """
    Close a position.

    Args:
        base_url: Base URL for the API
        token: Authentication token
        account_id: ID of the account
        contract_id: ID of the contract

    Returns:
        Response indicating success or failure
    """
    endpoint = "/Position/closeContract"
    body = {
        "accountId": account_id,
        "contractId": contract_id,
    }
    response = await make_request(BASE_URL=base_url, endpoint=endpoint, body=body, include_token=True, SESSION_TOKEN=token)
    return response


# Calculate TP and SL prices
def get_tp_sl_price(
    inst_type: str,
    entry_price: float,
    entry_order: str,
    take_profit_price: Optional[float] = None,
    stop_loss_price: Optional[float] = None,
    sl_dollar: Optional[float] = None,
    tp_dollar: Optional[float] = None,
    sl_percentage: Optional[float] = None,
    tp_percentage: Optional[float] = None,
    min_tick: float = 0.25
) -> tuple:
    """
    Calculate take-profit and stop-loss prices.

    Args:
        inst_type: Instrument type (e.g., 'FUT')
        entry_price: Entry price of the position
        entry_order: Order side ('BUY' or 'SELL')
        take_profit_price: Explicit take-profit price
        stop_loss_price: Explicit stop-loss price
        sl_dollar: Stop-loss in dollars
        tp_dollar: Take-profit in dollars
        sl_percentage: Stop-loss as a percentage
        tp_percentage: Take-profit as a percentage
        min_tick: Minimum tick size for price rounding

    Returns:
        Tuple of (take_profit_price, stop_loss_price)
    """
    tp = 0
    sl = 0
    if tp_dollar and not tp_percentage:
        tp = entry_price + tp_dollar if entry_order == 'BUY' else entry_price - tp_dollar
    elif not tp_dollar and tp_percentage:
        tp = entry_price + ((entry_price * tp_percentage) / 100) if entry_order == 'BUY' else entry_price - ((entry_price * tp_percentage) / 100)
    elif take_profit_price and not tp_dollar and not tp_percentage:
        tp = take_profit_price
    if sl_dollar and not sl_percentage:
        sl = entry_price - sl_dollar if entry_order == 'BUY' else entry_price + sl_dollar
    elif not sl_dollar and sl_percentage:
        sl = entry_price - ((entry_price * sl_percentage) / 100) if entry_order == 'BUY' else entry_price + ((entry_price * sl_percentage) / 100)
    elif stop_loss_price and not sl_dollar and not sl_percentage:
        sl = stop_loss_price
    tp = round(round(tp / min_tick) * min_tick, 10)
    sl = round(round(sl / min_tick) * min_tick, 10)
    return tp, sl


async def place_projectx_market_entry_and_oco(
    base_url: str,
    token: str,
    account_id: int,
    symbol_id: str,
    action: str,
    quantity: int,
    limit_price: Optional[float] = None,
    sl_price: Optional[float] = None,
    tp_price: Optional[float] = None,
    sl_dollar: Optional[float] = None,
    tp_dollar: Optional[float] = None,
    sl_percentage: Optional[float] = None,
    tp_percentage: Optional[float] = None,
    reverse_order_close: bool = False,
    duplicate_position_allow: bool = False,
    oco_url: str = 'https://userapi.topstepx.com/Order/editStopLoss',
    min_tick: float = 0.25,
    max_wait_time: int = 30,
    poll_interval: float = 0.2,
    log_key : str = ''
) -> Dict:
    """
    Place a market entry order, and if SL/TP parameters are provided, wait for it to be filled and place an OCO order.
    If action is 'CLOSE', close all positions and cancel all open orders for the given symbol.

    Args:
        base_url: Base URL for the API
        token: Authentication token
        account_id: ID of the account
        symbol_id: ID of the contract (symbol)
        action: Order side ('BUY', 'SELL', or 'CLOSE')
        quantity: Order quantity
        limit_price: Limit price for the order (if applicable)
        sl_price: Stop-loss price
        tp_price: Take-profit price
        sl_dollar: Stop-loss in dollars
        tp_dollar: Take-profit in dollars
        sl_percentage: Stop-loss as a percentage
        tp_percentage: Take-profit as a percentage
        reverse_order_close: If True, close all positions in opposite direction and open orders in same direction
        duplicate_position_allow: If False, prevent new positions if an open position exists in the same direction
        oco_url: URL for placing OCO orders
        min_tick: Minimum tick size for price rounding (default: 0.25)
        max_wait_time: Maximum time to wait for order to fill (seconds)
        poll_interval: Time between polling for order status (seconds)

    Returns:
        Dict containing order ID, position ID, OCO response (if applicable), and close/cancel results (for CLOSE action)
    """
    result = {"success": False, "order_id": None, "position_id": None, "oco_response": None, "error": None, "close_results": [], "cancel_results": [], 'tp_order_id': None, 'sl_order_id': None}
    logger.info(f'{log_key} started place_projectx_market_entry_and_oco for account {account_id}, symbol {symbol_id}, action {action}, quantity {quantity}, limit_price {limit_price}, sl_price {sl_price}, tp_price {tp_price}, sl_dollar {sl_dollar}, tp_dollar {tp_dollar}, sl_percentage {sl_percentage}, tp_percentage {tp_percentage}, reverse_order_close {reverse_order_close}, duplicate_position_allow {duplicate_position_allow}')
    try:
        # Validate action
        if action.upper() not in ["BUY", "SELL", "CLOSE"]:
            result["error"] = f"Invalid action: {action}. Must be 'BUY', 'SELL', or 'CLOSE'"
            logger.error(result["error"])
            return result

        # Handle CLOSE action
        if action.upper() == "CLOSE":
            logger.info(f'{log_key} CLOSE action initiated for symbol {symbol_id}')
            # Close all open positions for the symbol
            open_positions = await search_open_positions(base_url=base_url, token=token, account_id=account_id)
            for pos in open_positions:

                if pos.get("contractId") == symbol_id:
                    logger.info(f'{log_key} Closing position ID {pos.get("positionId")} for symbol {symbol_id}')
                    close_response = await close_position(
                        base_url=base_url,
                        token=token,
                        account_id=account_id,
                        contract_id=symbol_id
                    )
                    result["close_results"].append({
                        "position_id": pos.get("positionId"),
                        "success": close_response.get("success", False),
                        "response": close_response
                    })
                    if close_response.get("success", False):
                        logger.info(f"Closed position ID {pos.get('positionId')} for symbol {symbol_id}")
                    else:
                        logger.warning(f"Failed to close position ID {pos.get('positionId')} for symbol {symbol_id}: {close_response}")

            # Cancel all open orders for the symbol
            open_orders = await search_open_orders(base_url=base_url, token=token, account_id=account_id)
            for order in open_orders:
                if order.get("contractId") == symbol_id:
                    logger.info(f'{log_key} Cancelling order ID {order.get("id")} for symbol {symbol_id}')
                    cancel_response = await cancel_order(
                        base_url=base_url,
                        token=token,
                        account_id=account_id,
                        order_id=order.get("id")
                    )
                    result["cancel_results"].append({
                        "order_id": order.get("id"),
                        "success": cancel_response.get("success", False),
                        "response": cancel_response
                    })
                    if cancel_response.get("success", False):
                        logger.info(f"Cancelled order ID {order.get('id')} for symbol {symbol_id}")
                    else:
                        logger.warning(f"Failed to cancel order ID {order.get('id')} for symbol {symbol_id}: {cancel_response}")

            result["success"] = True
            logger.info(f"CLOSE action completed for symbol {symbol_id}: {len(result['close_results'])} positions closed, {len(result['cancel_results'])} orders cancelled")
            return result

        # Map action to side (0=Buy, 1=Sell) for BUY/SELL
        side = 0 if action.upper() == "BUY" else 1
        opposite_side = 1 if side == 0 else 0

        # Check for duplicate positions if duplicate_position_allow is False
        if not duplicate_position_allow:
            logger.info(f'{log_key} Checking for duplicate positions for symbol {symbol_id} in direction {action}')
            open_positions = await search_open_positions(base_url=base_url, token=token, account_id=account_id)
            logger.info(f'{log_key} Found {len(open_positions)} open positions for account {account_id}')
            for pos in open_positions:
                if pos.get("contractId") == symbol_id and ((side == 0 and pos.get('type') == 1) or (side == 1 and pos.get('type') == 2)):
                    logger.warning(f"Duplicate position detected for symbol {symbol_id} in direction {action}")
                    result["error"] = f"Duplicate position detected for symbol {symbol_id} in direction {action}"
                    logger.error(result["error"])
                    return result

        # Handle reverse_order_close if True
        if reverse_order_close:
            # Close opposite direction positions
            logger.info(f'{log_key} Reverse order close initiated for symbol {symbol_id}, opposite side {opposite_side}')
            open_positions = await search_open_positions(base_url=base_url, token=token, account_id=account_id)
            logger.info(f'{log_key} Found {len(open_positions)} open positions for account {account_id}')
            for pos in open_positions:
                if pos.get("contractId") == symbol_id and ((opposite_side == 0 and pos.get('type') == 1) or (opposite_side == 1 and pos.get('type') == 2)):
                    logger.info(f'{log_key} Closing opposite position ID {pos.get("positionId")} for symbol {symbol_id}')
                    close_response = await close_position(
                        base_url=base_url,
                        token=token,
                        account_id=account_id,
                        contract_id=symbol_id
                    )
                    if not close_response.get("success", False):
                        logger.warning(f"{log_key} Failed to close opposite position for symbol {symbol_id}: {close_response}")
                    else:
                        logger.info(f"{log_key} Closed opposite position for symbol {symbol_id}, position ID {pos.get('positionId')}")

            logger.info(f'{log_key} Cancelling open orders for symbol {symbol_id} in opposite direction')
            open_orders = await search_open_orders(base_url=base_url, token=token, account_id=account_id)
            logger.info(f'{log_key} Found {len(open_orders)} open orders for account {account_id}')
            for order in open_orders:
                if order.get("contractId") == symbol_id and order.get("side") == side:
                    logger.info(f'{log_key} Cancelling open order ID {order.get("id")} for symbol {symbol_id}')
                    cancel_response = await cancel_order(
                        base_url=base_url,
                        token=token,
                        account_id=account_id,
                        order_id=order.get("id")
                    )
                    if not cancel_response.get("success", False):
                        logger.warning(f"{log_key} Failed to cancel order ID {order.get('id')} for symbol {symbol_id}: {cancel_response}")
                    else:
                        logger.info(f"{log_key} Cancelled open order ID {order.get('id')} for symbol {symbol_id}")

        # Place market order (force trade_type to 2 for Market order)
        logger.info(f'{log_key} Placing market order for account {account_id}, symbol {symbol_id}, side {side}, quantity {quantity}, limit_price {limit_price}')
        order_id = await place_order(
            base_url=base_url,
            token=token,
            account_id=account_id,
            contract_id=symbol_id,
            order_type=2,  # Market order
            side=side,
            size=quantity,
            limitPrice=limit_price if limit_price else None
        )

        if not order_id:
            result["error"] = "Failed to place market order"
            logger.error(f"{log_key} Failed to place market order for account {account_id}, symbol {symbol_id}")
            return result

        result["order_id"] = order_id
        logger.info(f"{log_key} Placed market order ID {order_id} for account {account_id}, symbol {symbol_id}")

        # If no SL/TP parameters are provided, return early
        if not any([sl_price, tp_price, sl_dollar, tp_dollar, sl_percentage, tp_percentage]):
            result["success"] = True
            logger.info(f"{log_key} No SL/TP parameters provided for order {order_id}, skipping OCO and returning")
            return result

        # Wait for the order to reach a final status
        start_time = time.time()
        order_status = None
        current_time = datetime.datetime.utcnow()
        start_timestamp = (current_time - datetime.timedelta(minutes=5)).isoformat() + "Z"
        end_timestamp = (current_time + datetime.timedelta(minutes=5)).isoformat() + "Z"

        while time.time() - start_time < max_wait_time:
            logger.info(f"{log_key} Polling for order status for order ID {order_id}")
            orders = await search_all_orders(
                base_url=base_url,
                token=token,
                account_id=account_id,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp
            )
            logger.info(f"{log_key} Found {len(orders)} orders in the last 24 hours for account {account_id}")
            order = next((o for o in orders if o.get("id") == order_id), None)
            if order:
                logger.info(f"{log_key} Found order ID {order_id} with status {order.get('status')}")
                order_status = order.get("status")
                if order_status in [2, 3, 4, 5]:  # Filled, Cancelled, Expired, Rejected
                    break
            time.sleep(poll_interval)

        if not order_status:
            result["error"] = f"Order {order_id} not found within {max_wait_time} seconds"
            logger.error(result["error"])
            return result

        if order_status in [3, 4, 5]:
            status_map = {3: "Cancelled", 4: "Expired", 5: "Rejected"}
            result["error"] = f"Order {order_id} was {status_map[order_status]}"
            logger.info(result["error"])
            return result

        if order_status != 2:
            result["error"] = f"Order {order_id} not filled, current status: {order_status}"
            logger.error(result["error"])
            return result

        # Order is filled, get position
        open_positions = await search_open_positions(base_url=base_url, token=token, account_id=account_id)
        position = next((pos for pos in open_positions if pos.get("contractId") == symbol_id), None)

        if not position :
            result["error"] = f"{log_key} No position found for symbol {symbol_id} after order {order_id}"
            logger.error(result["error"])
            return result

        if ((side == 0 and position.get('type') == 1) or (side == 1 and position.get('type') == 2)):
            pass
        else:
            return result
        position_id = position.get("id")
        result["position_id"] = position_id
        logger.info(f"Found position ID {position_id} for symbol {symbol_id}")

        # Calculate and place OCO order
        entry_price = position.get("averagePrice")
        if not entry_price:
            result["error"] = "Entry price not found in position data"
            logger.error(result["error"])
            return result

        inst_type = "FUT"  # Adjust if needed
        logger.info(f"{log_key} Calculating TP/SL prices for position ID {position_id}, entry price {entry_price}")
        tp, sl = get_tp_sl_price(
            inst_type=inst_type,
            entry_price=entry_price,
            entry_order=action.upper(),
            take_profit_price=tp_price,
            stop_loss_price=sl_price,
            sl_dollar=sl_dollar,
            tp_dollar=tp_dollar,
            sl_percentage=sl_percentage,
            tp_percentage=tp_percentage,
            min_tick=min_tick
        )
        logger.info(f'{log_key} Calculated TP: {tp}, SL: {sl} for position ID {position_id}')
        if tp or sl:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            oco_data = {
                "positionId": position_id,
                "stopLoss": sl if sl else None,
                "takeProfit": tp if tp else None
            }
            if sl is None and tp is None:
                result["error"] = "Both SL and TP cannot be None"
                logger.error(result["error"])
                return result
            elif sl is None and tp is not None:
                oco_data = {
                    "positionId": position_id,
                    "takeProfit": tp
                }
            elif sl is not None and tp is None:
                oco_data = {
                    "positionId": position_id,
                    "stopLoss": sl
                }

            oco_data = {k: v for k, v in oco_data.items() if v is not None}

            try:
                logger.info(f"{log_key} Placing OCO order for position ID {position_id} with data: {oco_data}")
                response = requests.post(oco_url, headers=headers, json=oco_data)
                response_data = response.json()
                result["oco_response"] = response_data
                if response.status_code in (200, 201):

                    orders = await search_all_orders(
                        base_url=base_url,
                        token=token,
                        account_id=account_id,
                        start_timestamp=start_timestamp,
                        end_timestamp=end_timestamp
                    )
                    for order in orders:
                        if order.get('contractId') == symbol_id:
                            if order.get('status') == 1:
                                if order.get('type') == 1:
                                    tp_order_id = order.get('id')
                                    result["tp_order_id"] = tp_order_id
                                    logger.info(f'{log_key} TP order placed with ID {tp_order_id} for position {position_id}')
                                elif order.get('type') == 4:
                                    sl_order_id = order.get('id')
                                    result["sl_order_id"] = sl_order_id
                                    logger.info(f'{log_key} SL order placed with ID {sl_order_id} for position {position_id}')

                    result["success"] = True
                    logger.info(f"{log_key} OCO order placed for position {position_id}: {response_data}")
                else:
                    result["error"] = f"OCO order failed: {response_data}"
                    logger.error(result["error"])
            except Exception as e:
                result["error"] = f"Error placing OCO order: {str(e)}"
                logger.error(f"{log_key} Error placing OCO order: {traceback.format_exc()}")
        else:
            logger.info(f"{log_key} No valid TP/SL calculated for position {position_id}, skipping OCO")
            result["success"] = True

    except Exception as e:
        result["error"] = f"Error in place_market_entry_and_oco: {str(e)}"
        logger.error(f"Error in place_market_entry_and_oco: {traceback.format_exc()}")

    return result


async def fetch_and_save_projectx_instruments(user, connection_name):
    """
    Fetch and save ProjectX instruments for a user.

    Args:
        user: User object with id attribute
        connection_name: Name of the connection

    Returns:
        None
    """
    try:
        logger.info(f"Fetching all instruments for user {user.id}")
        user_multi_connection = get_multi_user_connections_by_connection_name(user.id, connection_name)
        all_ib_futures = get_ib_symbol_by_inst_type_list(['FUT'])
        all_futures = [futures.ib_symbol for futures in all_ib_futures]
        all_unique_futures = list(set(all_futures))
        if not user_multi_connection:
            logger.error(f"No multi user connection found for user {user.id} and connection name {connection_name}")
            return None
        projectx_api_key = user_multi_connection.connection_access_token
        if not projectx_api_key:
            logger.error(f"No projectx API key found for user {user.id} and connection name {connection_name}")
            return None
        BASE_URL = projectx_api_endpoints.get(user_multi_connection.connection_server)
        if not BASE_URL:
            logger.error(f"No BASE_URL found for connection server {user_multi_connection.connection_server}")
            return None
        for futures in all_unique_futures:
            logger.info(f"Fetching contract for symbol: {futures}")
            contracts = await search_contracts(base_url=BASE_URL, token=projectx_api_key, search_text=futures, live=False)
            for con in contracts:
                projectx_symbol = con['name']
                ib_entry = get_ib_trade_setting_for_user_by_local(projectx_symbol, 'FUT')
                if ib_entry:
                    logger.info(f"Found contract {con['name']} for local symbol {futures}")
                    ib_entry.projectx_id = con['id']
                    save_ib_trade_settings(ib_entry)
    except Exception as e:
        logger.error(f"Error in fetch_and_save_all_instruments: {traceback.format_exc()}")
        return None


async def refresh_all_projectx_token(data=None):
    """
    Refresh all ProjectX tokens for active connections.

    Args:
        data: Optional data (not used)

    Returns:
        None
    """
    all_projectx_connections = get_multi_user_by_engine('PROJECTX')
    for connection in all_projectx_connections:
        if connection.user_payment_id == -100 or connection.active == False:
            continue
        if connection.connection_datetime is not None:
            time_diff = (connection.connection_datetime - datetime.datetime.utcnow()).seconds
            connection_date = connection.connection_datetime.date()
            current_date = datetime.datetime.utcnow().date()
            if time_diff > 3600 and connection_date == current_date:
                continue
        projectx_api = projectx_api_endpoints.get(connection.connection_server)
        projectx_response = await projectx_authenticate(projectx_api, user_name=connection.connection_username,
                                                 api_key=connection.connection_password)
        account_id_data = {}
        if projectx_response and projectx_response['success']:
            auth_token = projectx_response.get('token')
            accounts = await search_accounts(base_url=projectx_api, token=auth_token, only_active_accounts=True)
            if accounts and len(accounts) > 0:
                for account in accounts:
                    account_id_data[account['name']] = account['id']
            account_id_string = json.dumps(account_id_data)
            update_multi_user_connection(id=connection.id, connection_access_token=auth_token,
                                        connection_account_id=account_id_string,
                                        connection_datetime=datetime.datetime.utcnow())



async def search_trades(
base_url: str, token: str,
        account_id: int,
) -> List[Dict]:
    """
    Search for trades for a specific account within a time range.

    Args:
        account_id: ID of the account
        start_timestamp: Start timestamp for the trade search (ISO 8601 format)
        end_timestamp: End timestamp for the trade search (ISO 8601 format), optional

    Returns:
        List of trade dictionaries
    """
    current_time = datetime.datetime.utcnow()
    start_timestamp = (current_time - datetime.timedelta(hours=24)).isoformat() + "Z"
    end_timestamp = (current_time + datetime.timedelta(hours=24)).isoformat() + "Z"
    endpoint = "/Trade/search"
    body = {
        "accountId": account_id,
        "startTimestamp": start_timestamp,
    }
    if end_timestamp:
        body["endTimestamp"] = end_timestamp

    response = await make_request(BASE_URL=base_url, SESSION_TOKEN=token, endpoint=endpoint, body=body, include_token=True)
    return response.get("trades", [])


# Example usage
# if __name__ == "__main__":
#     try:
#         # Example parameters
#         base_url = "https://api.topstepx.com"
#         token = "your_token_here"
#         account_id = 545
#         symbol_id = "CON.F.US.EP.M25"
# 
#         # Place market order with OCO
#         result = place_market_entry_and_oco(
#             base_url=base_url,
#             token=token,
#             account_id=account_id,
#             symbol_id=symbol_id,
#             trade_type=2,
#             action="BUY",
#             quantity=1,
#             sl_dollar=50.0,
#             tp_dollar=100.0,
#             min_tick=0.25
#         )
#         print("Market Entry and OCO Result:", json.dumps(result, indent=2))
# 
#         # Search accounts
#         accounts = search_accounts(base_url=base_url, token=token, only_active_accounts=True)
#         print("Accounts:", json.dumps(accounts, indent=2))
# 
#         # Search contracts
#         contracts = search_contracts(base_url=base_url, token=token, search_text="NQ", live=False)
#         print("Contracts:", json.dumps(contracts, indent=2))
# 
#         # Search open orders
#         open_orders = search_open_orders(base_url=base_url, token=token, account_id=account_id)
#         print("Open orders:", json.dumps(open_orders, indent=2))
# 
#         # Search all orders
#         current_time = datetime.datetime.utcnow()
#         start_timestamp = (current_time - datetime.timedelta(hours=24)).isoformat() + "Z"
#         end_timestamp = (current_time + datetime.timedelta(hours=24)).isoformat() + "Z"
#         all_orders = search_all_orders(
#             base_url=base_url,
#             token=token,
#             account_id=account_id,
#             start_timestamp=start_timestamp,
#             end_timestamp=end_timestamp
#         )
#         print("All orders:", json.dumps(all_orders, indent=2))
# 
#         # Place an order
#         order_id = place_order(
#             base_url=base_url,
#             token=token,
#             account_id=account_id,
#             contract_id=symbol_id,
#             order_type=1,  # Limit order
#             side=0,  # Buy
#             size=1,
#             limitPrice=21500
#         )
#         print("Order placed, ID:", order_id)
# 
#         # Cancel an order
#         if order_id:
#             cancel_response = cancel_order(base_url=base_url, token=token, account_id=account_id, order_id=order_id)
#             print("Order cancelled:", json.dumps(cancel_response, indent=2))
# 
#         # Search open positions
#         positions = search_open_positions(base_url=base_url, token=token, account_id=account_id)
#         print("Open positions:", json.dumps(positions, indent=2))
# 
#         # Close a position
#         close_response = close_position(base_url=base_url, token=token, account_id=account_id, contract_id=symbol_id)
#         print("Position closed:", json.dumps(close_response, indent=2))
# 
#     except Exception as e:
#         print(f"Error in main: {str(e)}")