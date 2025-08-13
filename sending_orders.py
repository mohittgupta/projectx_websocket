import json
import traceback

import asyncio
from fastapi import requests

from config import logger, front_backet_url, code_frontend, PROJECTX_Sending_ORDER_TYPE


async def sending_order(order_data,user_id,account_id,connection_name):
    try:
        logger.info(f"checking order for sending {order_data} for {user_id} {account_id} {connection_name}")
        side = order_data['side'] if 'side' in order_data else 0
        if side == 0:
            side = 'BUY'
        else:
            side = 'SELL'
        order_type = PROJECTX_Sending_ORDER_TYPE.get(order_data['type']) if 'type' in order_data else 'MKT'
        price = order_data['limit_price'] if 'limit_price' in order_data else 0
        if order_type == 'STP':
            price = order_data['stop_price'] if 'stop_price' in order_data else 0
        elif order_type == 'STPTRAIL':
            price = order_data['stop_price'] if 'stop_price' in order_data else 0

        if order_type == None:
            logger.info(f"Order type not found so sending MKT order, for {user_id} {account_id} {connection_name}")
            order_type = 'MKT'

        if order_data != None and order_data.get('status') == 2 and order_data.get('type') == 2:
            logger.info(f"Market Filled state Found for {user_id} {account_id} {connection_name}  {order_data}")
            if order_type =='STPTRAIL' and price == 0:
                logger.info(f"stptrail found  but price not found cannot send for {user_id} {account_id} {connection_name}  {order_data}")
                return

            order_dict = {'watch_user': user_id, 'main_order_id': order_data['order_id'], 'account_id': account_id,
                          'limit_price': 0,
                          'stp_price': 0,
                          'side': side,
                          'order_type': order_type,
                          'price': price,
                          'stop_price': order_data['stop_price'] if 'stop_price' in order_data else 0,
                          'quantity': order_data['size'] if 'size' in order_data else 0,
                          'tp_order_id': 0,
                          'tp_order_type': 0,
                          'tp_order_price': 0,
                          'sl_order_id': 0,
                          'sl_order_type': 0,
                          'sl_order_price': 0,
                          'text': 0,
                          'action': 'executing',
                          'contract_id': order_data['contract_id'] if 'contract_id' in order_data else 0
                          }
            await post_data(order_dict)
        elif order_data != None and order_data.get('status') == 1:
            logger.info(f"order state Open Found for {user_id} {account_id} {connection_name}  {order_data}")
            if order_type =='STPTRAIL' and price == 0:
                logger.info(f"stptrail found  but price not found cannot send for {user_id} {account_id} {connection_name}  {order_data}")
                return

            order_dict = {'watch_user': user_id, 'main_order_id': order_data['order_id'], 'account_id': account_id,
                          'limit_price': 0,
                          'stp_price':0,
                          'side': side,
                          'order_type': order_type,
                          'price': price,
                          'stop_price': order_data['stop_price'] if 'stop_price' in order_data else 0,
                          'quantity': order_data['size'] if 'size' in order_data else 0,
                          'tp_order_id': 0,
                          'tp_order_type': 0,
                          'tp_order_price': 0,
                          'sl_order_id': 0,
                          'sl_order_type':  0,
                          'sl_order_price':  0,
                          'text': 0,
                          'action': 'executing',
                          'contract_id': order_data['contract_id'] if 'contract_id' in order_data else 0
                          }
            await post_data(order_dict)
        elif order_data != None and order_data.get('status') == 3:
            logger.info(f"order state Cancelled Found for {user_id} {account_id} {connection_name}  {order_data}")
            order_dict = {'watch_user': user_id, 'main_order_id': order_data['order_id'], 'account_id': account_id,
                          'limit_price': 0,
                          'stp_price': 0,
                          'side': side,
                          'order_type': order_type,
                          'price': price,
                          'stop_price': order_data['stop_price'] if 'stop_price' in order_data else 0,
                          'quantity': order_data['size'] if 'size' in order_data else 0,
                          'tp_order_id':0,
                          'tp_order_type': 0,
                          'tp_order_price': 0,
                          'sl_order_id': 0,
                          'sl_order_type': 0,
                          'sl_order_price': 0,
                          'text': 0,
                          'action': 'canceling',
                          'contract_id': order_data['contract_id'] if 'contract_id' in order_data else 0
                          }
            await post_data(order_dict)
        elif order_data != None and order_data.get('status') == 4:
            logger.info(f"order state Expired Found for {user_id} {account_id} {connection_name}  {order_data}")
            order_dict = {'watch_user': user_id, 'main_order_id': order_data['order_id'], 'account_id': account_id,
                          'limit_price': 0,
                          'stp_price': 0,
                          'side': side,
                          'order_type': order_type,
                          'price': price,
                          'stop_price': order_data['stop_price'] if 'stop_price' in order_data else 0,
                          'quantity': order_data['size'] if 'size' in order_data else 0,
                          'tp_order_id':  0,
                          'tp_order_type': 0,
                          'tp_order_price': 0,
                          'sl_order_id': 0,
                          'sl_order_type': 0,
                          'sl_order_price': 0,
                          'text': 0,
                          'action': 'canceling',
                          'contract_id': order_data['contract_id'] if 'contract_id' in order_data else 0
                          }
            await post_data(order_dict)

    except Exception as e:
        logger.error(f" for {user_id} {account_id} {connection_name} error in sending msg  {traceback.format_exc()}")

async def post_data(order_dict):
    for x in range(0,3):
        try:
            logger.info(f"executing order {order_dict}")
            headers = {"Content-Type": "application/json"}
            # async with requests.AsyncClient() as client:
            #     response = await client.post(front_backet_url + 'watch-order-execute?code=' + code_frontend, data=json.dumps(order_dict), headers=headers)
            #     logger.error(f"Order Response: {response.text}  {order_dict}")
            break
        except Exception as e:
            logger.error(f"Error in post_data: {traceback.format_exc()}")
            await asyncio.sleep(0.1)