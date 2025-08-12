import traceback
from datetime import datetime

from config import logger
from db.crud_utils.projectx_utils.projectx_orders_utils import get_projectx_order_by_order_id
from db.crud_utils.projectx_utils.projectx_position_utils import get_projectx_position_by_position_id
from db.database import db_session
from db.models.projectx_data import Projectx_Orders, Projectx_Positions, Projectx_Trades


async def update_or_save_order_data(order_data_dict, unique_key):
    """
    Update or save order data in the database.

    Args:
        unique_key (str): Unique key to identify the order.
        order_data_dict (dict): Order data to be saved or updated.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    user_id = unique_key.split('_')[0]
    connection_name = unique_key.split('_')[1]
    account_id = unique_key.split('_')[2]
    order_data = {}
    for key, value in order_data_dict.items():
        if key == 'id':
            order_data['user_id'] = user_id
            order_data['connection_name'] = connection_name
            order_data['order_id'] = value
            order_data['update_server_time'] = datetime.utcnow()
        elif key == 'accountId':
            order_data['account_id'] = value
        elif key == 'contractId':
            order_data['contract_id'] = value
        elif key == 'creationTimestamp':
            order_data['creation_timestamp'] = value
        elif key == 'updateTimestamp':
            order_data['update_timestamp'] = value
        elif 'stopPrice' in key:
            order_data['stop_price'] = value
        elif 'fillVolume' in key:
            order_data['fill_volume'] = value
        elif key == 'limitPrice':
            order_data['limit_price'] = value
        elif key == 'type':
            order_data['type'] = value
        elif key == 'status':
            order_data['status'] = value
        elif key == 'side':
            order_data['side'] = value
        elif key == 'size':
            order_data['size'] = value
        elif key == 'price':
            order_data['price'] = value
        elif key == 'fees':
            order_data['fees'] = value

    try:
        existing_order = get_projectx_order_by_order_id(
            user_id=order_data['user_id'],
            connection_name=order_data['connection_name'],
            order_id=order_data['order_id']
        )
        print("order_data:", order_data)
        if existing_order:
            # Update existing order
            for key, value in order_data.items():
                setattr(existing_order, key, value)
            db_session.add(existing_order)
            db_session.commit()
            db_session.close()
        else:
            # Create new order
            new_order = Projectx_Orders(**order_data)
            db_session.add(new_order)
            db_session.commit()
            db_session.close()

        return True
    except Exception as e:
        print(f"Error updating or saving order data: {traceback.format_exc()}")
        logger.error(f"Error updating or saving order data: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return False


async def update_or_save_positions_data(position_data_dict, unique_key):
    """
    Update or save position data in the database.

    Args:
        unique_key (str): Unique key to identify the position.
        position_data_dict (dict): Position data to be saved or updated.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    user_id = unique_key.split('_')[0]
    connection_name = unique_key.split('_')[1]
    account_id = unique_key.split('_')[2]
    position_data = {}
    # {'id': 287945087, 'accountId': 8617480, 'contractId': 'CON.F.US.MNQ.U25', 'creationTimestamp': '2025-06-24T07:22:40.23633+00:00', 'type': 1, 'size': 1, 'averagePrice': 22355.25}}
    for key, value in position_data_dict.items():
        if key == 'id':
            position_data['user_id'] = user_id
            position_data['connection_name'] = connection_name
            position_data['position_id'] = value
            position_data['update_server_time'] = datetime.utcnow()
        elif key == 'accountId':
            position_data['account_id'] = value
        elif key == 'contractId':
            position_data['contract_id'] = value
        elif key == 'creationTimestamp':
            position_data['creation_timestamp'] = value
        elif key == 'type':
            position_data['type'] = value
        elif key == 'size':
            position_data['size'] = value
        elif key == 'averagePrice':
            position_data['average_price'] = value

    try:
        existing_position = get_projectx_position_by_position_id(
            user_id=position_data['user_id'],
            connection_name=position_data['connection_name'],
            position_id=position_data['position_id']
        )

        if existing_position:
            # Update existing position
            for key, value in position_data.items():
                setattr(existing_position, key, value)
            db_session.add(existing_position)
            db_session.commit()
            db_session.close()
        else:
            # Create new position
            new_position = Projectx_Positions(**position_data)
            db_session.add(new_position)
            db_session.commit()
            db_session.close()

        return True

    except Exception as e:
        print(f"Error updating or saving position data: {traceback.format_exc()}")
        logger.error(f"Error updating or saving position data: {traceback.format_exc()}")
        db_session.rollback()
        return False


async def update_or_save_trade_data(trade_data_dict, unique_key):
    """
    Update or save trade data in the database.

    Args:
        unique_key (str): Unique key to identify the trade.
        trade_data_dict (dict): Trade data to be saved or updated.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    user_id = unique_key.split('_')[0]
    connection_name = unique_key.split('_')[1]
    account_id = unique_key.split('_')[2]
    trade_data = {}

    for key, value in trade_data_dict.items():
        if key == 'id':
            trade_data['user_id'] = user_id
            trade_data['connection_name'] = connection_name
            trade_data['trade_id'] = value
            trade_data['update_server_time'] = datetime.utcnow()
        elif key == 'accountId':
            trade_data['account_id'] = value
        elif key == 'contractId':
            trade_data['contract_id'] = value
        elif key == 'creationTimestamp':
            trade_data['creation_timestamp'] = value
        elif key == 'price':
            trade_data['price'] = value
        elif key == 'fees':
            trade_data['fees'] = value
        elif key == 'side':
            trade_data['side'] = value
        elif key == 'size':
            trade_data['size'] = value
        elif key == 'voided':
            trade_data['voided'] = value
        elif key == 'orderId':
            trade_data['order_id'] = value

    try:
        existing_trade = db_session.query(Projectx_Trades).filter(
            Projectx_Trades.user_id == user_id,
            Projectx_Trades.connection_name == connection_name,
            Projectx_Trades.trade_id == trade_data['trade_id']
        ).first()

        if existing_trade:
            # Update existing trade
            for key, value in trade_data.items():
                setattr(existing_trade, key, value)

            db_session.add(existing_trade)
            db_session.commit()
            db_session.close()
        else:
            # Create new trade
            new_trade = Projectx_Trades(**trade_data)
            db_session.add(new_trade)
            db_session.commit()
            db_session.close()

        return True

    except Exception as e:
        print(f"Error updating or saving trade data: {traceback.format_exc()}")
        logger.error(f"Error updating or saving trade data: {traceback.format_exc()}")
        db_session.rollback()
        return False