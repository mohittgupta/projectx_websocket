import traceback

from business_logic.mail_utils import send_email
from config import logger, paddel_token
from db.crud_utils.multi_user_connection_utils.multi_user_read_utils import get_multi_user_connection_by_subscription_id
from db.crud_utils.subscription_utils.subscription_read import get_last_active_subscription, \
    get_all_active_subscription, get_last_active_subscription_sub_id
from db.crud_utils.subscription_utils.subscription_write import save_subscription_init
from db.crud_utils.user_payments_data.user_payment_data_utils import get_payment_data
from gateway.paddle_api import delete_paddel_subscription, subscription_paddel_Status, paddel_price_ino
from gateway.paypal_payment_api import get_auth_token, subscription_Status, delete_subscription, suspend_subscription


async def remove_active_subscription(user,sub_id):
    try:
        subs = await get_last_active_subscription_sub_id(user.user_name,sub_id)
        if subs == None:
            return "Active Subscription Not Found", True
        else:
            if subs.platform == "paddel":
                data = await delete_paddel_subscription(subs.paddle_sub_id, paddel_token)
                subs.status = 'MANUAL CANCELLED'
                await save_subscription_init(subs)
                # await send_email(user.user_name, subject="Don't Miss Out! Renew Your PickMyTrade Subscription Today",
                #            username="", msg_data=str(user.demo_expiry.date()), mail_type="demo_expiry_alert")
            else:
                token = await get_auth_token()
                if token != None:
                    data = await delete_subscription(subs.subscription_id,token)
                    subs.status = 'MANUAL CANCELLED'
                    await save_subscription_init(subs)
                    # await send_email(user.user_name, subject="Don't Miss Out! Renew Your PickMyTrade Subscription Today",  username="", msg_data=str(user.demo_expiry.date()), mail_type="demo_expiry_alert")
            return ["Subscription Cancelled"],False
    except Exception as e:
        logger.error(f"error in fetch_active_subscription {traceback.format_exc()}")
        return f"{e}", True

async def suspend_active_subscription_by_id(user,sub_id):
    try:
        subs = await get_last_active_subscription_sub_id(user.user_name,sub_id)
        if subs == None:
            return "Active Subscription Not Found", True
        else:
            if subs.platform == "paddel":
                # data = delete_paddel_subscription(subs.paddle_sub_id, paddel_token)
                subs.status = 'SUSPENDED'
                await save_subscription_init(subs)
            else:
                token = await get_auth_token()
                if token != None:
                    data = await suspend_subscription(subs.subscription_id,token)
                    subs.status = 'SUSPENDED'
                    await save_subscription_init(subs)
            return ["Subscription Suspended"],False
    except Exception as e:
        logger.error(f"error in fetch_active_subscription {traceback.format_exc()}")
        return f"{e}", True

async def fetch_active_subscription(user):
    try:
        res = []

        subs = get_all_active_subscription(user.user_name)
        logger.info(f"new subscriptions for user in db {subs}")

        if len(subs) < 0:
            return [], False
        else:
            token = await get_auth_token()
            for sub in subs:
                if sub.platform == "paddel":
                    data = await subscription_paddel_Status(sub.paddle_sub_id, paddel_token)
                    logger.info(f"subscription ststaus paddel {data}")

                    if data['scheduled_change'] != None and data['scheduled_change']['action'] == 'cancel':
                        data['status'] = 'CANCEL'

                    if data == None or data['status'].upper() != 'ACTIVE':
                        sub.status = 'NOT ACTIVE'
                        await save_subscription_init(sub)
                        # return res,True
                    else:
                        am = {"unit_price": {"amount": "100"}}
                        am = await paddel_price_ino(sub.plan_id)

                        dat = {"status": data['status'].upper(), "plan_id": sub.plan_id,
                               "start_time": data['started_at'], "id": sub.subscription_id,
                               "email_address": sub.email,
                               "last_payment": float(float(am['unit_price']['amount']) / 100),
                               "last_payment_time": data['items'][0]['previously_billed_at'],
                               "next_billing_time": data['items'][0]['next_billed_at'],
                               "currency_code": am['unit_price']['currency_code'], "given_name": "", "surname": "",
                               "type": "pad"}
                        res.append(dat)
                else:
                    if token != None:
                        data = await subscription_Status(sub.subscription_id, token)
                        logger.info(f"subscription ststaus paypal {data}")
                        if data == None or data['status'].upper() != 'ACTIVE':
                            sub.status = 'NOT ACTIVE'
                            await save_subscription_init(sub)
                            # return res,True
                        else:

                            multi_user_connection = get_multi_user_connection_by_subscription_id(sub.subscription_id)
                            try :
                                email_address = data['subscriber']['email_address'] if data[
                                                                                               'subscriber'] != None else ""
                            except Exception as e:
                                logger.error(f"error in fetch_active_subscription {traceback.format_exc()}")
                                email_address = ""
                            dat = {"status": data['status'], "plan_id": data['plan_id'],
                                   "start_time": data['start_time'], "id": data['id'],

                                   "email_address": email_address,
                                   "last_payment": data['billing_info']['last_payment']['amount']['value'],
                                   "currency_code": data['billing_info']['last_payment']['amount']['currency_code'],
                                   "last_payment_time": data['billing_info']['last_payment']['time'] if data[
                                                                                                            'billing_info'] != None else "",
                                   "next_billing_time": data['billing_info']['next_billing_time'] if data[
                                                                                                         'billing_info'] != None else "",
                                   "given_name": data['subscriber']['name']['given_name'] if data[
                                                                                                 'subscriber'] != None else "",
                                   "surname": data['subscriber']['name']['surname'] if data[
                                                                                           'subscriber'] != None else "",
                                   "type": "pay"}
                            if multi_user_connection != None:
                                dat["connection_name"] = multi_user_connection.connection_name
                            res.append(dat)
            return res, False
    except Exception as e:
        logger.error(f"error in fetch_active_subscription {traceback.format_exc()}")
        return [f"{str(e)}"], True



