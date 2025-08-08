import datetime
import json
import traceback
from dataclasses import asdict
from typing import Any

from config import logger, login_central_redis
from db.dtos.UserDto import UserDto


def convert_login_cen_into_dto(user):
    pass
    # try:
    #     logger.info(f"convert_login_cen_into_dto {user.id} {user.random_id}")
    #     udt = UserDto()
    #     udt.id = user.id
    #     udt.user_name = user.user_name
    #     udt.parent_mail = user.parent_mail
    #     udt.password = user.password
    #     udt.random_id = user.random_id
    #     udt.live_account_id = user.live_account_id
    #     udt.demo_account_id = user.demo_account_id
    #     udt.paid = user.paid
    #     udt.payment_in = user.payment_in
    #     udt.payment_exp = user.payment_exp
    #     udt.live_token = user.live_token
    #     udt.live_token_exp = user.live_token_exp
    #     udt.demo_token = user.demo_token
    #     udt.demo_token_exp = user.demo_token_exp
    #     udt.demo = user.demo
    #     udt.demo_expiry = user.demo_expiry
    #     udt.reset_link = user.reset_link
    #     udt.reset_link_exp = user.reset_link_exp
    #     udt.demo_account_name = user.demo_account_name
    #     udt.live_account_name = user.live_account_name
    #     udt.pause = user.pause
    #     udt.profit_goal = user.profit_goal
    #     udt.loss_goal = user.loss_goal
    #     udt.max_loss_created = user.max_loss_created
    #     udt.my_referral_code = user.my_referral_code
    #     udt.other_referral_code = user.other_referral_code
    #     udt.other_user_referral_code = user.other_user_referral_code
    #     udt.mail_verified = user.mail_verified
    #     udt.mail_verification_token = user.mail_verification_token
    #     udt.demo_mail_send = user.demo_mail_send
    #     udt.authtoken = user.authtoken
    #     udt.exetoken = user.exetoken
    #     udt.error_instruction_mail_flag = user.error_instruction_mail_flag
    #     udt.discount_promotional_flag = user.discount_promotional_flag
    #     udt.created = user.created
    #     udt.demo_disconnect_flag = user.demo_disconnect_flag
    #     udt.no_right_trade_flag = user.no_right_trade_flag
    #     udt.no_trade_flag = user.no_trade_flag
    #     udt.unsubscribe = user.unsubscribe
    #     udt.phone_no = user.phone_no
    #     udt.source = user.source
    #     udt.payment_mail = user.payment_mail
    #     udt.max_multi_account = user.max_multi_account
    #     udt.rollover_mail_send = user.rollover_mail_send
    #     u = convert_datetime_to_str(udt)
    #     login_central_redis.set(user.random_id, json.dumps(u),ex=36000)
    #     return udt
    # except Exception as e:
    #     logger.error(f"error in convert into dto logincentral {traceback.format_exc()}")
    # return None

def convert_datetime_to_str(obj: Any) -> dict:
    data = asdict(obj)
    for k, v in data.items():
        if isinstance(v, datetime.datetime):
            data[k] = v.isoformat()
    return data



def convert_dict_into_dto(user):
    try:
        udt = UserDto()
        udt.id = 0 if user['id'] == None or str(user['id']) == 'None' or str(user['id']) == 'null' else user['id']
        udt.user_name = None if user['user_name'] == None or str(user['user_name']) == 'None' or str(user['user_name']) == 'null' else user['user_name']
        udt.parent_mail = None if user['parent_mail'] == None or str(user['parent_mail']) == 'None' or str(user['parent_mail']) == 'null' else user['parent_mail']

        udt.password = None if user['password'] == None or str(user['password']) == 'None' or str(user['password']) == 'null' else user['password']
        udt.random_id = user['random_id']
        udt.live_account_id = None if user['live_account_id'] == None or str(user['live_account_id']) == 'None' or str(user['live_account_id']) == 'null' else user['live_account_id']
        udt.demo_account_id = None if user['demo_account_id'] == None or str(user['demo_account_id']) == 'None' or str(user['demo_account_id']) == 'null' else user['demo_account_id']
        udt.paid = None if user['paid'] == None or str(user['paid']) == 'None' or str(user['paid']) == 'null' else user['paid']
        payment_in = None if user['payment_in'] == None or str(
            user['payment_in']) == 'None' or str(
            user['payment_in']) == 'null' else user['payment_in']
        if payment_in != None:
            payment_in = payment_in.split(".")[0]
            payment_in = payment_in.replace("T"," ")
            payment_in = datetime.datetime.strptime(payment_in, '%Y-%m-%d %H:%M:%S')
        udt.payment_in = payment_in
        payment_exp = None if user['payment_exp'] == None or str(
            user['payment_exp']) == 'None' or str(
            user['payment_exp']) == 'null' else user['payment_exp']
        if payment_exp != None:
            payment_exp = payment_exp.split(".")[0]
            payment_exp = payment_exp.replace("T", " ")
            payment_exp = datetime.datetime.strptime(payment_exp, '%Y-%m-%d %H:%M:%S')
        udt.payment_exp = payment_exp
        udt.live_token = None if user['live_token'] == None or str(user['live_token']) == 'None' or str(user['live_token']) == 'null' else user['live_token']
        live_token_exp = None if user['live_token_exp'] == None or str(
            user['live_token_exp']) == 'None' or str(
            user['live_token_exp']) == 'null' else user['live_token_exp']
        if live_token_exp != None:
            live_token_exp = live_token_exp.split(".")[0]
            live_token_exp = live_token_exp.replace("T", " ")
            live_token_exp = datetime.datetime.strptime(live_token_exp, '%Y-%m-%d %H:%M:%S')
        udt.live_token_exp = live_token_exp
        udt.demo_token = None if user['demo_token'] == None or str(user['demo_token']) == 'None' or str(user['demo_token']) == 'null' else user['demo_token']

        demo_token_exp = None if user['demo_token_exp'] == None or str(
            user['demo_token_exp']) == 'None' or str(
            user['demo_token_exp']) == 'null' else user['demo_token_exp']
        if demo_token_exp != None:
            demo_token_exp = demo_token_exp.split(".")[0]
            demo_token_exp = demo_token_exp.replace("T", " ")
            demo_token_exp = datetime.datetime.strptime(demo_token_exp, '%Y-%m-%d %H:%M:%S')
        udt.demo_token_exp = demo_token_exp
        udt.demo = None if user['demo'] == None or str(user['demo']) == 'None' or str(user['demo']) == 'null' else user['demo']

        demo_expiry = None if user['demo_expiry'] == None or str(
            user['demo_expiry']) == 'None' or str(
            user['demo_expiry']) == 'null' else user['demo_expiry']
        if demo_expiry != None:
            demo_expiry = demo_expiry.split(".")[0]
            demo_expiry = demo_expiry.replace("T", " ")
            demo_expiry = datetime.datetime.strptime(demo_expiry, '%Y-%m-%d %H:%M:%S')
        udt.demo_expiry = demo_expiry
        udt.reset_link = None if user['reset_link'] == None or str(user['reset_link']) == 'None' or str(user['reset_link']) == 'null' else user['reset_link']

        reset_link_exp = None if user['reset_link_exp'] == None or str(
            user['reset_link_exp']) == 'None' or str(
            user['reset_link_exp']) == 'null' else user['reset_link_exp']
        if reset_link_exp != None:
            reset_link_exp = reset_link_exp.split(".")[0]
            reset_link_exp = reset_link_exp.replace("T", " ")
            reset_link_exp = datetime.datetime.strptime(reset_link_exp, '%Y-%m-%d %H:%M:%S')

        udt.reset_link_exp = reset_link_exp
        udt.demo_account_name = None if user['demo_account_name'] == None or str(user['demo_account_name']) == 'None' or str(user['demo_account_name']) == 'null' else user['demo_account_name']

        udt.live_account_name = None if user['live_account_name'] == None or str(user['live_account_name']) == 'None' or str(user['live_account_name']) == 'null' else user['live_account_name']
        udt.pause = None if user['pause'] == None or str(user['pause']) == 'None' or str(user['pause']) == 'null' else user['pause']
        udt.profit_goal = None if user['profit_goal'] == None or str(user['profit_goal']) == 'None' or str(user['profit_goal']) == 'null' else user['profit_goal']
        udt.loss_goal = None if user['loss_goal'] == None or str(user['loss_goal']) == 'None' or str(user['loss_goal']) == 'null' else user['loss_goal']
        udt.max_loss_created = None if user['max_loss_created'] == None or str(user['max_loss_created']) == 'None' or str(user['max_loss_created']) == 'null' else user['max_loss_created']
        udt.my_referral_code = None if user['my_referral_code'] == None or str(user['my_referral_code']) == 'None' or str(user['my_referral_code']) == 'null' else user['my_referral_code']
        udt.other_referral_code = None if user['other_referral_code'] == None or str(user['other_referral_code']) == 'None' or str(user['other_referral_code']) == 'null' else user['other_referral_code']

        udt.other_user_referral_code = None if user['other_user_referral_code'] == None or str(user['other_user_referral_code']) == 'None' or str(user['other_user_referral_code']) == 'null' else user['other_user_referral_code']
        udt.mail_verified = None if user['mail_verified'] == None or str(user['mail_verified']) == 'None' or str(user['mail_verified']) == 'null' else user['mail_verified']
        udt.mail_verification_token = None if user['mail_verification_token'] == None or str(user['mail_verification_token']) == 'None' or str(user['mail_verification_token']) == 'null' else user['mail_verification_token']

        demo_mail_send = None if user['demo_mail_send'] == None or str(
            user['demo_mail_send']) == 'None' or str(
            user['demo_mail_send']) == 'null' else user['demo_mail_send']
        if demo_mail_send != None:
            demo_mail_send = demo_mail_send.split(".")[0]
            demo_mail_send = demo_mail_send.replace("T", " ")
            demo_mail_send = datetime.datetime.strptime(demo_mail_send, '%Y-%m-%d %H:%M:%S')
        udt.demo_mail_send = demo_mail_send
        udt.authtoken = None if user['authtoken'] == None or str(user['authtoken']) == 'None' or str(user['authtoken']) == 'null' else user['authtoken']
        udt.exetoken = None if user['exetoken'] == None or str(user['exetoken']) == 'None' or str(user['exetoken']) == 'null' else user['exetoken']
        udt.error_instruction_mail_flag = None if user['error_instruction_mail_flag'] == None or str(user['error_instruction_mail_flag']) == 'None' or str(user['error_instruction_mail_flag']) == 'null' else user['error_instruction_mail_flag']

        discount_promotional_flag = None if user['discount_promotional_flag'] == None or str(user['discount_promotional_flag']) == 'None' or str(
            user['discount_promotional_flag']) == 'null' else user['discount_promotional_flag']
        if discount_promotional_flag != None:
            discount_promotional_flag = discount_promotional_flag.split(".")[0]
            discount_promotional_flag = discount_promotional_flag.replace("T", " ")
            discount_promotional_flag = datetime.datetime.strptime(discount_promotional_flag, '%Y-%m-%d %H:%M:%S')
        udt.discount_promotional_flag = discount_promotional_flag
        created = None if user['created'] == None or str(
            user['created']) == 'None' or str(
            user['created']) == 'null' else user['created']
        if created != None:
            created = created.split(".")[0]
            created = created.replace("T", " ")
            created = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
        udt.created = created
        demo_disconnect_flag = None if user['demo_disconnect_flag'] == None or str(
            user['demo_disconnect_flag']) == 'None' or str( user['demo_disconnect_flag']) == 'null' else user['demo_disconnect_flag']
        if demo_disconnect_flag != None:
            demo_disconnect_flag = demo_disconnect_flag.split(".")[0]
            demo_disconnect_flag = demo_disconnect_flag.replace("T", " ")
            demo_disconnect_flag = datetime.datetime.strptime(demo_disconnect_flag, '%Y-%m-%d %H:%M:%S')
        udt.demo_disconnect_flag = demo_disconnect_flag
        no_right_trade_flag = None if user['no_right_trade_flag'] == None or str(
            user['no_right_trade_flag']) == 'None' or str(user['no_right_trade_flag']) == 'null' else user[
            'no_right_trade_flag']
        if no_right_trade_flag != None:
            no_right_trade_flag = no_right_trade_flag.split(".")[0]
            no_right_trade_flag = no_right_trade_flag.replace("T", " ")
            no_right_trade_flag = datetime.datetime.strptime(no_right_trade_flag, '%Y-%m-%d %H:%M:%S')

        udt.no_right_trade_flag = no_right_trade_flag
        no_trade_flag = None if user['no_trade_flag'] == None or str(
            user['no_trade_flag']) == 'None' or str(user['no_trade_flag']) == 'null' else user[
            'no_trade_flag']
        if no_trade_flag != None:
            no_trade_flag = no_trade_flag.split(".")[0]
            no_trade_flag = no_trade_flag.replace("T", " ")
            no_trade_flag = datetime.datetime.strptime(no_trade_flag, '%Y-%m-%d %H:%M:%S')
        udt.no_trade_flag = no_trade_flag

        udt.unsubscribe = None if user['unsubscribe'] == None or str(user['unsubscribe']) == 'None' or str(user['unsubscribe']) == 'null' else user['unsubscribe']
        udt.phone_no = None if user['phone_no'] == None or str(user['phone_no']) == 'None' or str(user['phone_no']) == 'null' else user['phone_no']
        udt.source = None if user['source'] == None or str(user['source']) == 'None' or str(user['source']) == 'null' else user['source']
        payment_mail = None if user['payment_mail'] == None or str(user['payment_mail']) == 'None' or str(user['payment_mail']) == 'null' else user['payment_mail']
        if payment_mail != None:
            payment_mail = payment_mail.split(".")[0]
            payment_mail = payment_mail.replace("T", " ")
            payment_mail = datetime.datetime.strptime(payment_mail,'%Y-%m-%d %H:%M:%S')
        udt.payment_mail = payment_mail
        udt.max_multi_account = None if user['max_multi_account'] == None or str(user['max_multi_account']) == 'None' or str(user['max_multi_account']) == 'null' else user['max_multi_account']
        udt.rollover_mail_send = None if user['rollover_mail_send'] == None or str(user['rollover_mail_send']) == 'None' or str(user['rollover_mail_send']) == 'null' else user['rollover_mail_send']
        return udt
    except Exception as e:
        logger.error(f"error in convert into dto logincentral {traceback.format_exc()}")
    return None

