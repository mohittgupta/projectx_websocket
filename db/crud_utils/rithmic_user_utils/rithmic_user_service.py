import datetime
import traceback

import requests

from config import logger, rithmic_url, rithmic_app_name, rithmic_uri, rithmic_app_version
from db.crud_utils.login_central_utils.login_central_write_queries import save_prev_user
from db.crud_utils.multi_user_connection_utils.multi_user_read_utils import \
    get_multi_user_connections_by_connection_name
from db.crud_utils.trade_data_utils.trade_data_read_queries import get_trade_data_by_user_random_id
from db.crud_utils.trade_data_utils.trade_data_write_queries import save_trade_data
from db.crud_utils.user_payments_data.user_payment_data_utils import get_payment_data_by_id


async def save_rithmic_basket_id(user,alert_id,basket_id,type,status):
    try:
        logger.info(
            f"save basket id alert_id {alert_id} basket_id {basket_id} type {type} status {status}")
        alert_data = get_trade_data_by_user_random_id(user.random_id , alert_id)
        if alert_data == None:
            logger.info(f"Alert data not found Cannot save basket id alert_id {alert_id} basket_id {basket_id} type {type} status {status}")
        elif type == 'ENTRY':
            alert_data.entry_id = basket_id
            alert_data.entry_order_status = status
            alert_data.alert_status = 'Entry Order Submitted' if basket_id else status
            save_trade_data(alert_data)
        elif type == 'TP':
            alert_data.lmt_id = basket_id
            alert_data.entry_order_status = status
            save_trade_data(alert_data)
        elif type == 'SL':
            alert_data.stp_id = str(basket_id)
            alert_data.entry_order_status = status
            save_trade_data(alert_data)
        elif type == 'CANCELLED':
            alert_data.close_ids = str(basket_id)
            save_trade_data(alert_data)
        return f"Successfully saved",False
    except Exception as e:
        logger.error(f"error in basket id saving {traceback.format_exc()}")
        return f"Error {e}",True

async def save_rithmic_user_data(user,random_id,user_name,password,system_name,account,route,app_name,app_version,uri):
    try:
        res = requests.post(rithmic_url + "/rithmic_save_cred",
                            json={"user_key": random_id,"user_mail":user.user_name, "system_name": system_name,
                                  "password": password, "user_id": user_name,"account":account,"app_name":app_name,"route":route,"app_version":app_version,"uri":uri})
        logger.info(f"rithmic saved response {random_id} {res} user_name {user_name}")

        if system_name.upper() == 'RITHMIC PAPER TRADING' or system_name.upper() == 'RITHMIC TEST':
            user.demo = True
            await save_prev_user(user)
        else:
            user.demo = True
            await save_prev_user(user)
        return res.json()
    except Exception as e:
        logger.error(f"error in sving rithmic user {traceback.format_exc()}")
        return {"data": "Error in saving Rithmic Cred!", "error": True}

async def get_rithmic_user_data(random_id):
    try:
        res = requests.post(rithmic_url + "/rithmic_get_cred", json={"user_key": random_id})
        logger.info(f"Rithmic get response {random_id} {res}")
        return res.json()
    except Exception as e:
        logger.error(f"error in sving rithmic user {traceback.format_exc()}")
        return {"data": "Error in getting Rithmic Cred!", "error": True}


async def delete_rithmic_user_data(random_id):
    try:
        res = requests.post(rithmic_url + "/rithmic_delete_cred", json={"user_key": random_id})
        logger.info(f"Rithmic delete response {random_id} {res}")
        return res.json()
    except Exception as e:
        logger.error(f"error in sving rithmic user {traceback.format_exc()}")
        return {"data": "Error in getting Rithmic Cred!", "error": True}

async def login_rithmic_user_data(random_id):
    try:
        res = requests.post(rithmic_url+"/rithmic_login",json={"user_key": random_id })
        logger.info(f"rithmic login response {random_id} {res}")
        return res.json()
    except Exception as e:
        logger.error(f"error in saving rithmic user {traceback.format_exc()}")
        return {"data": "Error in Rithmic Login!", "error": True}


async def disconnect_rithmic_user_data(random_id):
    try:
        res = requests.post(rithmic_url+"/rithmic_logout",json={"user_key": random_id })
        logger.info(f"rithmic disconnect response {random_id} {res}")
        return res.json()
    except Exception as e:
        logger.error(f"error in sving rithmic user {traceback.format_exc()}")
        return {"data": "Error in Rithmic Login!", "error": True}


async def ping_rithmic_user_data(random_id):
    try:
        res = requests.post(rithmic_url+"/ping_rithmic",json={"user_key": random_id })
        logger.info(f"rithmic ping response {random_id} {res}")
        return res.json()
    except Exception as e:
        logger.error(f"error in sving rithmic user {traceback.format_exc()}")
        return {"data": "Error in Rithmic Login!", "error": True}

async def get_rithmic_user_validation_data(user, connection_name):
    user_multi_connection = get_multi_user_connections_by_connection_name(user.id, connection_name)
    # if user.demo == False and not user.paid:
    # send_email(user.user_name, subject="HFT Tradovate", username="", msg_data="HFT Tradovate - Subscription Not Found, Can Not Place Order")
    # save_trade_data_msg(d, token, 'Subscription Not Found, Can Not Place Order', user)
    # return {"data": "Subscription Not Found", "error": True}, 200, False
    if user_multi_connection is None:
        return False
    elif user_multi_connection:
        payment_id = user_multi_connection.user_payment_id
        payment_data = get_payment_data_by_id(payment_id)
        if payment_data is None:
            return False
        elif payment_data.expire_by.date() < datetime.datetime.now().date():
            return False
        return True


async def save_rithmic_cred_by_coonection(user, user_key, connection_environment,
                                         connection_username, connection_password,
                                         connection_server, connection_account_number):
    try:
        # create_multi_user_connection(user.id, -100, '', connection_name, 'RITHMIC',connection_environment=request_json['route'].lower(),
#                                          connection_username=request_json['user_name'], connection_password=request_json['password'],
#                                          connection_account_number=None, connection_server=request_json['system_name'], active=False)

        msg = await save_rithmic_user_data(user, user_key, connection_username,
                                           connection_password, connection_server,
                                           connection_account_number, connection_environment,
                                           rithmic_app_name.get(connection_server), rithmic_app_version,
                                           rithmic_uri.get(connection_server))

        if msg.get('error') == False:
            msg = await login_rithmic_user_data(user_key)

        return msg
    except Exception as e:
        logger.error(f"error in saving rithmic user {traceback.format_exc()}")
        return {"data": "Error in saving Rithmic Cred!", "error": True}