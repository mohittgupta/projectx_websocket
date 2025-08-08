import asyncio
import datetime
import json
import traceback

import requests

from business_logic.tradovate_connector import reverse_order_type_convert, get_symbol_from_contract_Id, get_account_id, \
    get_tradovate_open_order, get_tradovate_position, liquidiate_position, get_list_account_id
from config import logger, tradovate_sock_url, tradovate_sock_unique_code
from db.crud_utils.login_central_utils.login_central_read_queries import get_by_random_key, get_by_user_main_key
from db.crud_utils.multi_account_utils.multi_account_read import get_by_id_multi_acc, get_by_user_id_multi_acc
from db.crud_utils.multi_account_utils.multi_account_write import save_multi_accounts_in_db, del_multi_accounts_in_db
from db.crud_utils.tradovate_accounts_utils.tradovate_accounts_read import get_tradovate_accounts_by_user_id_name
from db.crud_utils.tradovate_accounts_utils.tradovate_accounts_service import add_tradovate_accounts

from db.crud_utils.watch_client_order_id_map_utils.watch_client_order_id_map_read import get_wast_map_by_master_token
from db.models.multi_accounts import multi_accounts


async def save_multi_account_row(user,master_user,master_account_id,active,token,account_id,risk_percentage,quantity_multiplier,id,fixed_quantity):
    try:
        if id == 0:
            ta = multi_accounts()
            ta.user_random_id = user.id
            ta.master_user = master_user
            ta.master_account_id = master_account_id
            ta.active = active
            ta.created = datetime.datetime.now()
            ta.status = False
            ta.token = token
            ta.account_id = account_id
            ta.multiplier = quantity_multiplier
            ta.risk_percentage = risk_percentage
            ta.fixed_quantity = int(fixed_quantity)
            await save_multi_accounts_in_db(ta)
            return {"data": 'Successfully Insert', "error": False}
        else:
            ta = await get_by_id_multi_acc(id,user.id)
            if ta != None:
                if ta.status:
                    return {"data": 'Cannot modify in running mode.', "error": False}
                ta.user_random_id = user.id
                ta.master_user = master_user
                ta.master_account_id = master_account_id
                ta.active = active
                ta.token = token
                ta.account_id = account_id
                ta.multiplier = quantity_multiplier
                ta.risk_percentage = risk_percentage
                ta.fixed_quantity = int(fixed_quantity)
                await save_multi_accounts_in_db(ta)
                return {"data": 'Successfully Update', "error": False}
            else:
                return {"data": 'Invalid ID', "error": True}

    except Exception as e:
        logger.error(f"error in saving multi accounts {traceback.format_exc()}")
        return {"data":e,"error":True}



async def fetch_multi_account(user):
    try:
        data = []
        ta = await get_by_user_id_multi_acc(user.id)
        for t in ta:
            data.append({"token":t.token,"master_account_id":t.master_account_id,"master_user":t.master_user,"id":t.id,"account_id":t.account_id,"active":t.active,
                         "status":'Running' if t.status else 'Stopped',
                         "risk_percentage":t.risk_percentage,"quantity_multiplier":t.multiplier,"fixed_quantity":t.fixed_quantity})
        return {"data":data, "error": False}
    except Exception as e:
        logger.error(f"error in fetching multi accounts {traceback.format_exc()}")
        return {"data":[],"error":True}


async def remove_multi_account(id,user):
    try:
        logger.info(f"user deleting multiaccount {user.random_id}")
        ta = await get_by_id_multi_acc(id, user.id)
        if ta != None:
            if ta.status:
                return {"data": 'Cannot modify in running mode.', "error": False}
            await del_multi_accounts_in_db(ta)
        return {"data":'Successfully Removed', "error": False}
    except Exception as e:
        logger.error(f"error in removing multi accounts {traceback.format_exc()}")
        return {"data":e,"error":True}

async def getting_token(user):
    try:
        token = []
        if (datetime.datetime.now() > user.demo_expiry):
            logger.info(f"user account expired cannot send token {user.random_id}    {user.demo}")
            await stop_copier_websocket(user)
        elif user.demo and user.demo_token != None  and user.demo_token != "":
            logger.info(f"we are reconnecting websocket user is demo {user.random_id}")
            token.append(user.demo_token)
        elif (not user.demo) and user.live_token != None and user.live_token != "":
            logger.info(f"we are reconnecting websocket user is live {user.random_id}")
            token.append(user.live_token)
        else:
            logger.info(f"token not found so  stopping websocket {user.random_id}    {user.demo}")
            await stop_copier_websocket(user)

        ta = await get_by_user_id_multi_acc(user.id)
        account_list = []
        for t in ta:
            tv_accounts = await get_tradovate_accounts_by_user_id_name(t.master_user, t.master_account_id)
            if tv_accounts == None or tv_accounts.tradovate_account_id == "":
                account_id, account_name = await get_account_id(user, t.master_account_id)
                logger.info(
                    f"getting_token adding account in user from tv for watch {t.master_user} account_id {account_id}  account_name {account_name} master_account_id {t.master_account_id}")
                if account_id != "" and str(account_id) != "":
                    account_id = str(account_id)
                    account_list.append(int(account_id))
            else:
                logger.info(
                    f"getting_token adding account in user from db for watch {t.master_user} {tv_accounts.tradovate_account_id}    {t.master_account_id}")
                account_list.append(int(tv_accounts.tradovate_account_id))
            # -------
        return token,account_list,False
    except Exception as e:
        logger.error(f"error in start websocket {traceback.format_exc()}")
        return [],[],True

async def get_copier_order_map(user,from_date,to_date):
    try:
        from_date = datetime.datetime.strptime(from_date+" 00:00:01", '%Y-%m-%d %H:%M:%S'),
        to_date = datetime.datetime.strptime(to_date+" 23:59:59", '%Y-%m-%d %H:%M:%S')
        datas = await get_wast_map_by_master_token(user.random_id,from_date,to_date)
        result = {}
        for data in datas:
            if result.get(data.master_order_id) == None:
                result.update({data.master_order_id:{"child_order":[{"order_id":data.child_order_id,"account_id":data.child_account_id,"msg":data.msg }],"master_account_id":data.master_account_id,"datetime":str(data.datetime)}})
            else:
                res = result.get(data.master_order_id)
                child_order = res['child_order']
                child_order.append({"order_id":data.child_order_id,"account_id":data.child_account_id,"msg":data.msg} )
                result.update({data.master_order_id: {"child_order": child_order, "datetime": str(data.datetime)}})

        return {"data": result, "error": False}
    except Exception as e:
        logger.error(f"error in copier get_order_map {traceback.format_exc()}")
        return {"data":str(e),"error":True}

async def closing_child_position(user):
    try:
        logger.info(f"flat on start for {user.random_id}")
        ta = await get_by_user_id_multi_acc(user.id)
        for t in ta:
            currentt_user = user
            tradovate_account_id = ""
            symbol_need_to_close = []
            open_orders, positions = None, None
            if currentt_user.random_id == t.token:
                tradovate_account_id = await get_tradovate_accounts_by_user_id_name(currentt_user.random_id, t.account_id)
                if tradovate_account_id != None:
                    tradovate_account_id = tradovate_account_id.tradovate_account_id
                else:
                    logger.info(f"cannot close child account id not found for {currentt_user.random_id} {t.account_id}")
                open_orders = await get_tradovate_open_order(currentt_user)
                positions = await get_tradovate_position(currentt_user)
            else:
                logger.info(f"in flat on differrent child token found {t.token}")
                currentt_user = await get_by_user_main_key(t.token)
                if currentt_user != None:
                    tradovate_account_id = await get_tradovate_accounts_by_user_id_name(currentt_user.random_id, t.account_id)
                    if tradovate_account_id != None:
                        tradovate_account_id = tradovate_account_id.tradovate_account_id
                    else:
                        logger.info(
                            f"cannot close child account id not found for {currentt_user.random_id} {t.account_id}")
                    open_orders = await get_tradovate_open_order(currentt_user)
                    positions = await get_tradovate_position(currentt_user)
                else:
                    logger.info(f"in flat invalid child token  {t.token}")
            logger.info(f"open_orders {open_orders}")
            logger.info(f"positions {positions}")
            if open_orders != None:
                for open_order in open_orders:
                    if (open_order['ordStatus'] == 'Working' or open_order['ordStatus'] == 'Suspended') and str(
                            open_order['accountId']) == str(tradovate_account_id) and (
                    not open_order['contractId'] in symbol_need_to_close):
                        logger.info(f"open order id found {open_order['contractId']}")
                        symbol_need_to_close.append(open_order['contractId'])
            if positions != None:
                for position in positions:
                    if position['netPos'] != 0:
                        if str(position['accountId']) == str(tradovate_account_id) and (
                        not position['contractId'] in symbol_need_to_close):
                            logger.info(f"position id found {position['contractId']}")
                            symbol_need_to_close.append(position['contractId'])
            for contract in symbol_need_to_close:
                logger.info(
                    f"closing child position / orders tradovate_account_id {tradovate_account_id}   contract {contract}")
                error_text, orderId = await liquidiate_position(currentt_user, tradovate_account_id, contract)
                # save_trade_data_msg_for_watch(symbol, side, user_req, token, status, user, order_type="MKT")
                logger.info(f"liquidate_position response error_text {error_text} orderId {orderId}")
        return f"Successfully Closed", False
    except Exception as e:
        logger.error(f"Exception in closing child orders, positions {traceback.format_exc()}")
        return f"Contact to Administrator, please close your order/position manually. {str(e)}", True


async def start_copier_websocket(user):
    try:
        logger.info(f"running start_copier_websocket {user.random_id}")
        token = ""
        if user.demo and user.demo_token != None  and user.demo_token != "":
            token = user.demo_token
        elif (not user.demo) and user.live_token != None and user.live_token != "":
            token = user.live_token
        else:
            logger.info(f"cannot strat websocket demo token not found {user.random_id}")
            return f"Can not Start Tradovate Token Not Found", True

        #  saving new ids   in db
        account_list = await get_list_account_id(user)
        for ac in account_list:
            logger.info(f"saving latest accounts in db...{user.random_id} {ac}")
            await add_tradovate_accounts(user.random_id, str(ac['id']), str(ac['name']))
        logger.info(f"latest account save done {user.random_id}")
        already_running = False
        ta = await get_by_user_id_multi_acc(user.id)
        account_list = []
        for t in ta:
            master_account_id_name = t.master_account_id
            # getting account id
            tv_accounts = await get_tradovate_accounts_by_user_id_name(t.master_user,t.master_account_id)
            if tv_accounts == None or tv_accounts.tradovate_account_id == "":
                account_id,account_name = await get_account_id(user,t.master_account_id)
                logger.info(
                    f"adding account in user from tv for watch {t.master_user} account_id {account_id}  account_name {account_name} master_account_id {t.master_account_id}")
                if account_id != "" and str(account_id) != "":
                    account_id = str(account_id)
                    account_list.append(int(account_id))
            else:
                logger.info(f"adding account in user from db for watch {t.master_user} {tv_accounts.tradovate_account_id}    {t.master_account_id}")
                account_list.append(int(tv_accounts.tradovate_account_id))

            # -------

            if t.status:
                already_running = True
                break
            t.status = True
            await save_multi_accounts_in_db(t)
        if len(ta) == 0:
            return f"Multi Account Mapping Not Found.", True
        if (not already_running):
            logger.info(f"start_copier_websocket accessing url {user.random_id}")
            headers = {"Content-Type": "application/json"}


            r = requests.post(tradovate_sock_url+'/start_websocket',json={"code":tradovate_sock_unique_code,"url":'wss://demo.tradovateapi.com/v1/websocket' if user.demo else 'wss://live.tradovateapi.com/v1/websocket',
                                                                                     "watch_user":user.random_id,"token":token,
                                                                                     "demo":user.demo,"accounts":account_list },headers=headers)
            logger.info(f"response of start socket {user.random_id} {r}")
            return f"Start Done",False
        else:
            return f"Already Running , Disconnect First.", True
    except Exception as e:

        logger.error(f"error in start websocket {traceback.format_exc()}")
        return f"Please Re-Connect tradovate account.",True


async def stop_copier_websocket(user):
    try:
        logger.info(f"stopping stop_copier_websocket {user.random_id}")
        ta = await get_by_user_id_multi_acc(user.id)
        for t in ta:
            t.status = False
            await save_multi_accounts_in_db(t)
        headers = {"Content-Type": "application/json"}
        r = requests.post(tradovate_sock_url + '/stop_websocket', json={"code":tradovate_sock_unique_code,"watch_user": user.random_id}, headers=headers)
        logger.info(f"response of stop socket {user.random_id} {r}")
        return f"Stop Done",False
    except Exception as e:
        logger.error(f"error in stop websocket {traceback.format_exc()}")
        return f"Cannot stop, {e}, Contact to Administrator.",True

async def copier_status(user):
    try:
        logger.info(f"getting status of copier_websocket {user.random_id}")
        headers = {"Content-Type": "application/json"}
        r = requests.post(tradovate_sock_url + '/status_websocket', json={"code":tradovate_sock_unique_code,"watch_user": user.random_id}, headers=headers)
        logger.info(f"response of socket status {user.random_id} {r}")
        return r.json()['data'],r.json()['error']
    except Exception as e:
        logger.error(f"error in stop websocket {traceback.format_exc()}")
        return f"Cannot stop, {e}, Contact to Administrator.",True


# async def exit_position_for_watch_user(cl,watch_user,json_data):
#     try:
#         account_id = ""
#         if cl.account_id != None and cl.account_id != "":
#             account_id = cl.account_id
#         contract = ""
#         try:
#             contract = json_data['details'].split('Contract:')[1]
#         except Exception as e:
#             logger.info(f"watch contract not found for exit position {watch_user} {json_data}")
#             return {"data": "Contract Not Found.", "error": True}
#         header = {'content-type': 'application/json'}
#         res = requests.post('http://localhost:5000/add-trade-data-latest', json={
#             "symbol": contract.strip(),
#             "data": 'CLOSE',
#             "quantity": 1,
#             "risk_percentage": 0,
#             "price": 0,
#             "tp": 0,
#             "sl": 0,
#             "percentage_tp": 0,
#             "dollar_tp": 0,
#             "dollar_sl": 0,
#             "order_type": 0,
#             "account_id": account_id,
#             "percentage_sl": 0,
#             "trail": 0,
#             "trail_stop": 0,
#             "trail_trigger": 0,
#             "trail_freq": 0,
#             "update_tp": False,
#             "update_sl": False,
#             "token": cl.token,
#             "duplicate_position_allow": True,
#             "reverse_order_close": False
#         }, headers=header)
#         logger.info(f"Close place order response {res}")
#         return {"data": f"Successfully Placed {cl.token}", "error": False}
#     except Exception as e:
#         logger.error(f"error in exit_position_for_watch_user clients {traceback.format_exc()}")
#         return {"data": e, "error": True}
# async def watch_order_executing(cl,watch_user,json_data):
#     try:
#         user=None
#         if json_data['types'] == 'ExitPosition':
#             msg = await exit_position_for_watch_user(cl,watch_user,json_data)
#             return msg
#         params = json.loads(json_data['params'])
#         quantity = params['entryVersion']['orderQty']
#         ordertype = reverse_order_type_convert(params['entryVersion']['orderType'])
#         stp_price = params['brackets'][0]['stopLoss'] if (
#                     'brackets' in params and len(params['brackets']) > 0 and 'stopLoss' in params['brackets'][0]) else 0
#         limit_price = params['brackets'][0]['profitTarget'] if (
#                     'brackets' in params and len(params['brackets']) > 0 and 'profitTarget' in params['brackets'][
#                 0]) else 0
#         if stp_price != 0:
#             stp_price = abs(stp_price)
#         if limit_price != 0:
#             limit_price = abs(limit_price)
#         json_data['params'] = json.dumps(params)
#         symbol = await get_symbol_from_contract_Id(user, json_data['contractId'])
#         risk_percen = 0
#         if cl.multiplier != 0:
#             quantity = quantity * cl.multiplier
#         elif cl.risk_percentage != 0:
#             quantity = 0
#             risk_percen = cl.risk_percentage
#         account_id = ""
#         if cl.account_id != None and cl.account_id != "":
#             account_id = cl.account_id
#         header = {'content-type': 'application/json'}
#         res = requests.post('http://localhost:5000/add-trade-data', json={
#             "symbol": symbol,
#             "data": json_data['action'],
#             "quantity": quantity,
#             "risk_percentage": risk_percen,
#             "price": params['entryVersion']['price'],
#             "tp": 0,
#             "sl": 0,
#             "percentage_tp": 0,
#             "dollar_tp": limit_price,
#             "dollar_sl": stp_price,
#             "order_type": ordertype,
#             "account_id": account_id,
#             "percentage_sl": 0,
#             "trail": 0,
#             "trail_stop": 0,
#             "trail_trigger": 0,
#             "trail_freq": 0,
#             "update_tp": False,
#             "update_sl": False,
#             "token": cl.token,
#             "duplicate_position_allow": True,
#             "reverse_order_close": False
#         }, headers=header)
#         logger.info(f"place order response {res}")
#         return {"data": f"Successfully Placed {cl.token}", "error": False}
#     except Exception as e:
#         logger.error(f"error in executing clients {traceback.format_exc()}")
#         return {"data": e, "error": True}