import datetime
import traceback
from business_logic.mail_utils import send_email
from config import logger, sender_mail, default_engine, supported_broker, paddel_frontend_callback, frontend_url
from db.crud_utils.login_central_utils.login_central_read_queries import get_by_demo_from_to_date, get_all_users, \
    get_by_user_name
from db.crud_utils.login_central_utils.login_central_write_queries import save_prev_user
from db.crud_utils.mail_trigger_utils.mail_trigger_read import get_triggers_by_user_id
from db.crud_utils.mail_trigger_utils.mail_trigger_write import save_triggers
from db.crud_utils.subscription_utils.subscription_read import get_created_only, get_last_active_subscription
from db.crud_utils.subscription_utils.subscription_write import save_subscription_init
from db.crud_utils.trade_data_utils.trade_data_read_queries import all_trades_by_user, all_trades_by_user_no_trade, \
    all_trades_by_user_entry_found
from db.models.mail_trigger import mail_trigger
from gateway.paddle_api import create_user_subscription


async def half_hour_mail():
    try:
        logger.info(f"half_hour_mail thread running {datetime.datetime.now()}")
        subscriptions_data = await get_created_only()
        users_for_mail= []
        for sub in subscriptions_data:
            logger.info(f"subs mail found for checking {sub.email}")
            if datetime.datetime.now() >  (sub.server_created_time + datetime.timedelta(minutes=30)):
                if sub.email in users_for_mail:
                    sub.mail_send = True
                    logger.info(f"payment issue mail already send to support so we will not send  again {sub.mail_send} sub main id {sub.id}")
                    await save_subscription_init(sub)
                else:
                    created_date = sub.server_created_time.date()
                    active_user = await get_last_active_subscription(sub.email)
                    logger.info(
                        f"payment issue mail send checking {sub.email}  sub main id active_user")
                    if active_user == None or (active_user.server_created_time.date() != created_date):
                        logger.info(
                            f"payment issue mail sending to support {sub.email}  sub main id {sub.id}")
                        try:
                            user_obj = await get_by_user_name(sub.email)
                            paddeldata, error = await create_user_subscription(user_obj, sub.subscription_id_json,by_mail=True)
                            logger.info(f"for mail paddel link generate {sub.email} {sub.subscription_id_json} paddeldata {paddeldata}")
                            paddel_link = paddel_frontend_callback+'?_ptxn=' + paddeldata.split('_ptxn=')[1]
                            user_data_dict = {"paddel_link":paddel_link}
                            await send_email(sub.email, subject=f"PickMyTrade Payment issue!",
                                       username=sub.email, msg_data=sub.amount,
                                       mail_type="payment_issue_only_support",user_data_dict=user_data_dict)
                        except Exception as e:
                            logger.error(f"error in paddel link generate for mail {traceback.format_exc()}")
                    users_for_mail.append(sub.email)
                    sub.mail_send = True
                    await save_subscription_init(sub)

    except Exception as e:
        logger.error(f"error in half hour mail {traceback.format_exc()}")
    logger.info(f"half_hour_mail thread done {datetime.datetime.now()}")

async def condition_demo_mail_send():
    try:
        users = await get_all_users()
        for user in users:
            if (user.mail_verified and user.created != None and (user.created + datetime.timedelta(days=1)) <= datetime.datetime.now() and
                    user.demo_token_exp == None and user.demo_disconnect_flag == None and user.paid == False):
                #  sending mail need to connect tradovate...
                if not user.unsubscribe:
                    await send_email(user.user_name, subject=f"Action Required: Connect to {supported_broker.get(default_engine)} for Automated Trading", username="",
                               msg_data=str(user.demo_expiry.date()), mail_type="tradovate_connected_check")
                user.demo_disconnect_flag = datetime.datetime.now()
                await save_prev_user(user)
                continue
            if (user.mail_verified and user.created != None and (
                    user.created + datetime.timedelta(days=2)) <= datetime.datetime.now() and
                    user.demo_token_exp != None and user.no_trade_flag == None and user.paid == False):
                trades = all_trades_by_user_no_trade(user.random_id)
                if len(trades) == 0:
                    if not user.unsubscribe:
                        await send_email(user.user_name,
                                   subject="Action Required: Final Steps to Configure Your Automated Trading",
                                   username="", msg_data=str(user.demo_expiry.date()), mail_type="no_trade")
                    user.no_trade_flag = datetime.datetime.now()
                    await save_prev_user(user)
                    continue
                else:
                    logger.info(f"demo account ok trade send so we will check no_trade_flag flag {user.user_name}")
                    user.no_trade_flag = datetime.datetime.now()
                    await save_prev_user(user)
                    continue

            if (user.mail_verified and user.created != None and (user.created + datetime.timedelta(days=2)) <= datetime.datetime.now() and
                    user.demo_token_exp != None and user.no_right_trade_flag == None and user.paid == False):
                # sending no right trade alert...
                trades = all_trades_by_user(user.random_id)
                msg = []
                for trade in trades:
                    msg.append({"alert_status":trade.alert_status , "alert":trade.alert_data,"entry_order_status":trade.entry_order_status,"trade_time":trade.trade_time})
                if len(msg) > 0:
                    if not user.unsubscribe:
                        await send_email(sender_mail, subject=f"{supported_broker.get(default_engine)} No right Trade, Entry Id not Found",
                                   username=user.user_name,msg_data=msg, mail_type="no_right_trade")
                    user.no_right_trade_flag = datetime.datetime.now()
                    await save_prev_user(user)
                    continue
                else:
                    t = all_trades_by_user_entry_found(user.random_id)
                    if len(t) > 0:
                        logger.info(f"demo account ok trade send so we will not check right trade flag {user.user_name}")
                        user.no_right_trade_flag = datetime.datetime.now()
                        await save_prev_user(user)
                        continue

            if user.mail_verified and user.paid and user.demo_expiry.date() < datetime.datetime.now().date():
                logger.info(f"live expired removing paid flag {str(user.demo_expiry.date())}")
                if not user.unsubscribe:
                    await send_email(user.user_name, subject="Don't Miss Out! Renew Your PickMyTrade Subscription Today",
                               username="", msg_data=str(user.demo_expiry.date()), mail_type="demo_expiry_alert")
                user.paid = False
                await save_prev_user(user)
                continue
            if (user.mail_verified) and (not user.paid) and (user.demo_expiry != None) and ( (user.demo_expiry + datetime.timedelta(days=3)).date() <= datetime.datetime.now().date()   ) and user.discount_promotional_flag == None:
                logger.info(f"currently commented! sending promotional mail {str(user.demo_expiry.date())} {user.user_name}")
                # if not user.unsubscribe:
                #     send_email(user.user_name, subject="🎉 Special Offer: 10% Off Your PickMyTrade Renewal! 🎉",username="",
                #                msg_data=str(user.demo_expiry.date()), mail_type="discount_promotional_flag")
                # user.discount_promotional_flag = datetime.datetime.now()
                # save_prev_user(user)
                continue

    except Exception as e:
        logger.error(f"error in condition mail send {traceback.format_exc()}")

async def mail_send(from_date,to_date):
    try:
        if from_date == "":
            from_date = datetime.datetime.now() - datetime.timedelta(days=2)
            to_date = datetime.datetime.now()
        else:
            from_date = datetime.datetime.strptime(from_date,"%Y-%m-%d")
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d")
        users = await get_by_demo_from_to_date(from_date,to_date)
        i=0
        users_found = []
        for ut in users:
            if(not ut.paid  ) and (ut.demo_mail_send ==None ) and ut.mail_verified:
                logger.info(f"sending demo exp mail to {ut.user_name}")
                users_found.append(ut.user_name)
                if not ut.unsubscribe:
                    await send_email(ut.user_name, subject="Don't Miss Out! Renew Your PickMyTrade Subscription Today", username="",
                               msg_data=str(ut.demo_expiry.date()),mail_type="demo_expiry_alert")
                i=i+1
                ut.demo_mail_send = datetime.datetime.now()
                await save_prev_user(ut)
        return f"Send mail to {i} user {users_found}",False
    except Exception as e:
        logger.error(f"{traceback.format_exc()}")
        return e,True


async def mail_verification_send(email):
    try:
        user = await get_by_user_name(email)
        if user == None:
            return {"data": f"Invalid email id!", "error": True}
        elif user.mail_verified == True:
            return {"data": f"Your email has already been verified. Please log in.", "error": True}
        elif user.mail_verification_token == None:
            return {"data": f"Verification token not found. Contact to administrator.", "error": True}
        else:
            trigger_detail = await get_triggers_by_user_id(user.id)
            if trigger_detail == None:
                trigger_detail = mail_trigger()
                trigger_detail.user_id = user.id
                await send_email(user.user_name, subject='Welcome to PickMyTrade!', username=email,
                                 msg_data=frontend_url + "/#/mail_verified?token=" + user.mail_verification_token,
                                 mail_type='register')
                trigger_detail.mail_verification_link_send = datetime.datetime.now()
                await save_triggers(trigger_detail)
            elif  (trigger_detail != None and trigger_detail.mail_verification_link_send != None
                   and datetime.datetime.now() < (trigger_detail.mail_verification_link_send + datetime.timedelta(minutes=10))):
                return {"data":"Please wait 15 minutes before requesting a new email verification link.", "error": True}
            elif (trigger_detail != None):
                await send_email(user.user_name, subject='Welcome to PickMyTrade!', username=email,
                                 msg_data=frontend_url + "/#/mail_verified?token=" + user.mail_verification_token,
                                 mail_type='register')
                trigger_detail.mail_verification_link_send = datetime.datetime.now()
                await save_triggers(trigger_detail)
        return {"data":"We have sent a verification email to your inbox. Please check both your Inbox and Spam folder to verify your email address.","error":False}
    except Exception as e:
        logger.error(f"{traceback.format_exc()}")
        return {"data": f"Something is going wrong, contact to administrator. {str(e)}", "error": True}
