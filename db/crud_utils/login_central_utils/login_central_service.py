import asyncio
import datetime
import json
import random
import string
import threading
import traceback
from collections import OrderedDict
from dataclasses import asdict
from typing import Any

from business_logic.encode_decode import generate_salted_hash
from business_logic.object_factory import bridge_ping
from config import reset_link, frontend_url, default_engine, supported_broker
from business_logic.mail_utils import send_email
from business_logic.tradovate_connector import get_account_value,  place_order, get_contract
from config import logger
from db.crud_utils.brokers_utils.brokers_read_utils import get_all_brokers

from db.crud_utils.login_central_utils.login_central_read_queries import get_by_user_name, get_by_random_key, \
    get_by_user_name_password, get_by_reset_link, get_by_mail_token, get_by_referral_id, get_by_account_not_verified, \
    get_by_users_name, get_by_user_email
from db.crud_utils.login_central_utils.login_central_write_queries import save_new_user, save_prev_user
from db.crud_utils.multi_account_utils.multi_account_read import get_by_user_id_multi_acc
from db.crud_utils.multi_account_utils.multi_account_write import save_multi_accounts_in_db
from db.crud_utils.multi_user_connection_utils.multi_user_read_utils import get_multi_user_connections_brokers_by_id
from db.crud_utils.order_data_utils.order_data_read import get_by_order_id_by_user_id
from db.crud_utils.order_data_utils.order_data_write import save_order_details
from db.crud_utils.sub_account_utils.sub_account_write import save_sub_accounts
from db.crud_utils.sub_account_utils.sub_accounts_read import get_total_sub_accounts
from db.crud_utils.trade_data_utils.trade_data_read_queries import all_trades_by_user_no_trade
from db.crud_utils.trade_data_utils.trade_data_write_queries import save_trade_data
from db.crud_utils.trade_setting_utils.trade_setting_read_queries import get_setting_by_random_id
from db.crud_utils.trade_setting_utils.trade_setting_write_queries import add_initial_common_settings, \
    save_trade_setting_db
from db.crud_utils.tradovate_accounts_utils.tradovate_accounts_read import get_tradovate_accounts_by_userid
from db.crud_utils.tradovate_accounts_utils.tradovate_accounts_write import save_tradovate_accounts
from db.crud_utils.user_brokers_utils.user_brokers_write_utils import delete_user_broker
from db.crud_utils.user_payments_data.user_payment_data_utils import get_payment_data_by_id
from utils.password_utils import get_hashed_password, verify_password


async def disconnect_tradovate(user):
    try:
        logger.info(f"user want to disconnect tradovate {user.user_name}")
        user.live_token = None
        user.live_token_exp = None
        user.demo_token = None
        user.demo_token_exp = None
        await save_prev_user(user)
        return {"data": "Successfully Disconnect", "error": False}
    except Exception as e:
        logger.error(f"error in reset Password {traceback.format_exc()}")
        return {"data":f"Error in Disconnecting Tradovate  {e}","error":True}

async def regenrate_main_key(user):
    try:

        new_key = ''
        while True:
            new_key = generate_salted_hash(user.user_name+""+str(datetime.datetime.now()))
            key_user = await get_by_random_key(new_key)
            if key_user == None:
                break
            else:
                logger.info(f"Duplicated key generate in regenrate function {new_key}")

        old_key = user.random_id
        logger.info(f"user want to regenrate key {user.user_name} old_key {old_key} new_key {new_key}")
        user.random_id = new_key
        await save_prev_user(user)
        logger.info(f"old_key {old_key} new_key {new_key} save user done for regenerate key ")

        setting = get_setting_by_random_id(old_key)
        for st in setting:
            st.random_id = new_key
            save_trade_setting_db(st)
        logger.info(f"old_key {old_key} new_key {new_key} user setting done for regenerate key ")
        order_data_details = get_by_order_id_by_user_id(old_key)
        for od in order_data_details:
            od.user_id = new_key
            await save_order_details(od)
        logger.info(f"old_key {old_key} new_key {new_key} user order data done for regenerate key ")

        multi_acc_data = await get_by_user_id_multi_acc(old_key)
        for ma in multi_acc_data:
            ma.master_user = new_key
            await save_multi_accounts_in_db(ma)
        logger.info(f"old_key {old_key} new_key {new_key} user multi account data done for regenerate key ")

        tds = all_trades_by_user_no_trade(old_key)
        for td in tds:
            td.user_id = new_key
            save_trade_data(td)
        logger.info(f"old_key {old_key} new_key {new_key} user trade data done for regenerate key ")

        tasd = get_tradovate_accounts_by_userid(old_key)
        for tg in tasd:
            tg.user_random_id = new_key
            await save_tradovate_accounts(tg)
        logger.info(f"old_key {old_key} new_key {new_key} user tradovate accounts done for regenerate key ")

        return {"data": new_key, "error": False}
    except Exception as e:
        logger.error(f"error in reset Password {traceback.format_exc()}")
        return {"data":f"Error in generating key  {e}","error":True}


async def set_new_password(code,password):
    try:
        login_user = await get_by_reset_link(code)
        if login_user == None or password == "":
            logger.info(f"{code} user not  found")
            return {"data": "User Not Found,Try Again with New Code", "error": True}
        elif login_user.reset_link_exp == None or login_user.reset_link_exp < datetime.datetime.now():
            logger.info(f"{code} token expired")
            return {"data": "Token Expired,Try Again with New Code", "error": True}
        else:
            logger.info(f"{login_user.id} adding new password code {code}  {password}")
            login_user.password = password
            login_user.password_hash = get_hashed_password(password)
            login_user.reset_link = None
            login_user.reset_link_exp = None
            await save_prev_user(login_user)
            return {"data": "Password Changed!", "error": False}
    except Exception as e:
        logger.error(f"error in reset Password {traceback.format_exc()}")
        return {"data":f"Error in Reset Password  {e}","error":True}


async def send_reset_link(email):
    try:
        logger.info(f"sending reset link to {email}")
        email =email.strip()
        email = email.lower()
        login_user = await get_by_user_name(email)
        if login_user == None:
            logger.info(f"{email} user not  found")
            return {"data": "Mail Id Not Found.", "error": True}
        else:

            random_key = generate_salted_hash(email + "" + str(datetime.datetime.now()))
            login_user.reset_link = random_key
            login_user.reset_link_exp = datetime.datetime.now() + datetime.timedelta(hours=3)
            await save_prev_user(login_user)
            await send_email(email, subject='Password Reset Request at PickMyTrade!', username="",  msg_data=reset_link+"?code="+random_key,mail_type='reset_link')
            return {"data": "Reset Link Sent, Please Check Your Mail ID", "error": False}
    except Exception as e:
        logger.error(f"error in reset Passwordlink {traceback.format_exc()}")
        return {"data":f"Error in Reset Password Link {e}","error":True}

async def mail_verification_check(token):
    try:
        logger.info(f"mail verification start for token {token}")
        user = await get_by_mail_token(token)
        if user == None:
            return "Invalid Token", True
        else:
            if user.mail_verified == None or user.mail_verified == False:
                email = user.user_name
                random_id = user.random_id
                user.demo_expiry = datetime.datetime.now() + datetime.timedelta(days=5)
                user.mail_verified = True
                await save_prev_user(user)
                await send_email(email, subject="Next Steps: Connect Broker" +" and Create Alerts!", username=email,
                           msg_data=random_id,  mail_type='mail_verified_done')
            return "Successfully Verified", False
    except Exception as e:
        logger.error(f"error in mail verification {traceback.format_exc()}")
        return "Error in mail verification, contact to administrator",True

async def signup_user(email,password,phone_no,source,other_user_referral_code):
    try:
        email =email.strip()
        email = email.lower()
        login_user = await get_by_user_name(email)
        if login_user != None:
            logger.info(f"{email} user already exist")
            return {"data": "User Already Exist", "error": True}
        else:
            if other_user_referral_code != "":
                other_user = await get_by_referral_id(other_user_referral_code)
                if other_user == None:
                    logger.info(f"{email} invalid refreel code {other_user_referral_code}")
                    # return {"data": "Invalid Referral Code", "error": True}
            random_key=''
            while True:
                random_key = generate_salted_hash(email + "" + str(datetime.datetime.now()))
                key_user = await get_by_random_key(random_key)
                if key_user == None:
                    break
                else:
                    logger.info(f"Duplicated key generate in function {random_key}")

            referral_id = ''
            while True:
                referral_id = generate_salted_hash(email + "rfl" + str(datetime.datetime.now()))
                key_user = await get_by_referral_id(referral_id)
                if key_user == None:
                    break
                else:
                    logger.info(f"Duplicated key generate in function {random_key}")

            logger.info(f"creating new user {email}")
            password_hash = get_hashed_password(password)
            verification_key = await save_new_user(email,password,password_hash,random_key,referral_id , phone_no,source,other_user_referral_code)
            logger.info(f"new user saving done {email}")
            await send_email(email, subject='Welcome to PickMyTrade!', username=email,
                       msg_data=frontend_url+"/#/mail_verified?token="+verification_key,mail_type='register')
            # try:
            #     asyncio.create_task(add_initial_common_settings(random_key))
            #     # threading.Thread(target=add_initial_common_settings,args=(random_key,)).start()
            #     # add_initial_common_settings(random_key)
            # except Exception as e:
            #     logger.error(f"error in saving user  {traceback.format_exc()}")
            return {"data": "Successfully Saved", "error": False}
    except Exception as e:
        logger.error(f"error in signup {traceback.format_exc()}")
        return {"data":f"Error in User Registration {e}","error":True}


async def get_user_profile(key_user):
    try:
        user_data = []
        all_brokers = get_all_brokers()
        for broker in all_brokers:

            broker_name = broker.broker_name
            broker_id = broker.broker_id
            demo_exipry = None
            live_expiry = None
            subscription_id = None
            connect, error, status = True , None , None
            broker_connected = False
            all_user_broker_by_id = get_multi_user_connections_brokers_by_id(key_user.id, broker_id)
            all_user_broker_by_id = list(set(all_user_broker_by_id))
            if all_user_broker_by_id is not None and len(all_user_broker_by_id) > 0:
                for user_broker_by_id in all_user_broker_by_id:
                    given_payment_id = user_broker_by_id.user_payment_id
                    payment_data = get_payment_data_by_id(given_payment_id)
                    given_sub_id = payment_data.subscription_id
                    if payment_data is None:
                        delete_user_broker(user_broker_by_id)
                        break
                    elif payment_data.expire_by.date() >= datetime.datetime.now().date():
                        demo_exipry = payment_data.demo_expiry
                        live_expiry = payment_data.expire_by
                        subscription_id = payment_data.subscription_id
                        broker_connected = True
                        break
            user_broker_data = OrderedDict([
                ("Id" , key_user.id),
                ('Email', key_user.user_name),
                ('Key', key_user.random_id),
                ('Broker', broker_name),
                ('Broker Id', broker_id),
                ('Demo Expiry', demo_exipry.strftime("%Y-%m-%d") if demo_exipry is not None else None),
                ('Payment Expiry', live_expiry.strftime("%Y-%m-%d") if live_expiry is not None else None),
                ('Subscription ID', subscription_id),
                ('Broker Connected', broker_connected),
                ('Local App Connected', connect),
                ('Demo', key_user.demo),

            ])
            user_data.append(user_broker_data)
        return user_data
    except Exception as e:
        logger.error(f"error in User Profile {traceback.format_exc()}")
        return []


async def get_rithmic_user_profile(key_user):
    try:
        if key_user == None:
            return {"data": f"User Not Found", "error": True}
        live_token_Expired = True if key_user.live_token_exp == None or (datetime.datetime.now()> key_user.live_token_exp) else False
        demo_token_Expired = True if key_user.demo_token_exp == None or  (datetime.datetime.now() > key_user.demo_token_exp) else False

        connect,error,status = await bridge_ping(key_user,'RITHMIC')
        demo_exipry = key_user.demo_expiry
        live_expiry = key_user.payment_exp
        all_user_broker_by_id = get_multi_user_connections_brokers_by_id(key_user.id, 1)
        all_user_broker_by_id = list(set(all_user_broker_by_id))
        if all_user_broker_by_id is not None and len(all_user_broker_by_id) > 0:
            for user_broker_by_id in all_user_broker_by_id:
                given_payment_id = user_broker_by_id.user_payment_id
                payment_data = get_payment_data_by_id(given_payment_id)
                given_sub_id = payment_data.subscription_id
                logger.info(f"payment data {payment_data}")
                try:
                    if payment_data is None:
                        delete_user_broker(user_broker_by_id)
                        break
                    elif payment_data.expire_by.date() >= datetime.datetime.now().date():
                        demo_exipry = payment_data.demo_expiry
                        live_expiry = payment_data.expire_by
                        subscription_id = payment_data.subscription_id
                        broker_connected = True
                        break
                except Exception as e:
                    logger.error(f"payment data error {payment_data} , expiry {payment_data.expire_by} , date {datetime.datetime.now().date()}")

                    logger.error(f"error in User Profile {traceback.format_exc()}")
                    return {"data":f"Error in User Profile {e}","error":True}
        return {"data": {"is_broker_connected":connect ,"demo":key_user.demo,"username":key_user.user_name,"user_key":key_user.random_id ,"paid":key_user.paid ,"subscription_expiry":live_expiry ,
                         "live_token_Expired":live_token_Expired,"demo_token_Expired":demo_token_Expired,"account_id":key_user.demo_account_name if key_user.demo else key_user.live_account_name ,
                         "account_value":0,"demo_Expiry":demo_exipry,'pause':key_user.pause,
                         'profit_amount':key_user.profit_goal,'loss_amount':key_user.loss_goal,'discount_code':key_user.other_referral_code,
                         'other_referral':key_user.other_user_referral_code,'my_referral':key_user.my_referral_code ,"status":status  }, "error": False}
    except Exception as e:
        logger.error(f"error in User Profile {traceback.format_exc()}")
        return {"data":f"Error in User Profile {e}","error":True}

async def get_ib_user_profile(key_user):
    try:
        if key_user == None:
            return {"data": f"User Not Found", "error": True}
        live_token_Expired = True if key_user.live_token_exp == None or (datetime.datetime.now()> key_user.live_token_exp) else False
        demo_token_Expired = True if key_user.demo_token_exp == None or  (datetime.datetime.now() > key_user.demo_token_exp) else False

        connect,error, status = True, None, None
        demo_exipry = key_user.demo_expiry
        live_expiry = key_user.payment_exp
        all_user_broker_by_id = get_multi_user_connections_brokers_by_id(key_user.id, 2)
        all_user_broker_by_id = list(set(all_user_broker_by_id))
        if all_user_broker_by_id is not None and len(all_user_broker_by_id) > 0:
            for user_broker_by_id in all_user_broker_by_id:
                given_payment_id = user_broker_by_id.user_payment_id
                payment_data = get_payment_data_by_id(given_payment_id)
                given_sub_id = payment_data.subscription_id
                logger.info(f"payment data {payment_data}")
                if payment_data is None:
                    delete_user_broker(user_broker_by_id)
                    break
                elif payment_data.expire_by.date() >= datetime.datetime.now().date():
                    demo_exipry = payment_data.demo_expiry
                    live_expiry = payment_data.expire_by
                    subscription_id = payment_data.subscription_id
                    broker_connected = True
                    break
        return {"data": {"is_broker_connected":connect ,"demo":key_user.demo,"username":key_user.user_name,"user_key":key_user.random_id ,"paid":key_user.paid ,"subscription_expiry":live_expiry ,
                         "live_token_Expired":live_token_Expired,"demo_token_Expired":demo_token_Expired,"account_id":key_user.demo_account_name if key_user.demo else key_user.live_account_name ,
                         "account_value":0,"demo_Expiry":demo_exipry,'pause':key_user.pause,
                         'profit_amount':key_user.profit_goal,'loss_amount':key_user.loss_goal,'discount_code':key_user.other_referral_code,
                         'other_referral':key_user.other_user_referral_code,'my_referral':key_user.my_referral_code ,"status":status  }, "error": False}
    except Exception as e:
        logger.error(f"error in User Profile {traceback.format_exc()}")
        return {"data":f"Error in User Profile {e}","error":True}

async def save_account_status(live,key_user):
    try:
        ta = await get_by_user_id_multi_acc(key_user.id)
        already_running = False
        for t in ta:
            if t.status:
                already_running = True
                break
        if already_running:
            return {"data": f"Cannot Switch , Firstly Stop Trade Copier.", "live": False if key_user.demo else True, "error": True}
        key_user.demo = False if live else True
        await save_prev_user(key_user)
        return {"data": f"Status Changed","live":live, "error": False}
    except Exception as e:
        logger.error(f"error in save_account_status {traceback.format_exc()}")
        return {"data":f"Error in Account Status {e}","error":True}

async def order_paused_unpaused(pause,profit_amount,loss_amount,key_user):
    try:
        key_user.pause = True if pause else False
        key_user.profit_goal = float(profit_amount)
        key_user.loss_goal = float(loss_amount)

        await save_prev_user(key_user)
        return {"data": f"Order Status Changed","pause":pause, "error": False}
    except Exception as e:
        logger.error(f"error in save_account_status {traceback.format_exc()}")
        return {"data":f"Error in Order Status {e}","error":True}


async def login_user(email,password,exe_request=False, admin_request= False):
    try:
        email =email.strip()
        email = email.lower()
        socket_url=""
        u= get_by_user_email(email)

        if (u == None):
            return {"data": "Invalid Credential", "error": True}

        user_verified = verify_password(password , u.password_hash)

        if (u == None) or not user_verified:
            print("Invalid Credential")
            return {"data": "Invalid Credential", "error": True}
        elif (u.mail_verified == None or u.mail_verified == False):
            return {"data": "We have sent a verification email to your inbox. Please check both your Inbox and Spam folder to verify your email address.", "error": True, "mail_verification": False}
        else:
            random_id = u.random_id
            token =  generate_salted_hash(email + "" + str(datetime.datetime.now()))
            if exe_request:
                u.exetoken = token
            elif admin_request:
                u.admin_token = token
            else:
                u.authtoken =token
            await save_prev_user(u)
            return {"data": token,"socket_url":socket_url,'id':random_id,  "error": False}
    except Exception as e:
        logger.error(f"error in signup {traceback.format_exc()}")
        return {"data":f"Error in User Login {e}","error":True}


async def add_pass_hash_for_user(user):
    password = user.password
    hash_pass = get_hashed_password(password)
    user.password_hash = hash_pass
    await save_prev_user(user)
    return True



async def send_verification_mail(email):
    try:
        logger.info(f"sending account mail verification link to {email}")
        email =email.strip()
        email = email.lower()
        login_user = None
        if email != '':
            login_user = await get_by_users_name(email)
        else:
            login_user = await get_by_account_not_verified()

        if login_user == None:
            logger.info(f"{email} user not  found")
            return {"data": "Mail Id Not Found.", "error": False}
        else:
            for u in login_user:
                if u.mail_verified != True and u.mail_verification_token != None:
                        await send_email(u.user_name, subject='Welcome to PickMyTrade!', username=email,
                                         msg_data=frontend_url + "/#/mail_verified?token=" + u.mail_verification_token,
                                         mail_type='register')
                        u.mail_verification_token = None
                        await save_prev_user(u)
            return {"data": f"Mail Send Done for {len(login_user)} user", "error": False}
    except Exception as e:
        logger.error(f"error in reset Passwordlink {traceback.format_exc()}")
        return {"data":f"Error in Sending Mail {e}","error":True}