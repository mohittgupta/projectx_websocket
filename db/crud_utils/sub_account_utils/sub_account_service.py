import datetime
import random
import string
import traceback
import uuid

from business_logic.encode_decode import generate_salted_hash
from business_logic.mail_utils import send_email
from config import logger
from db.crud_utils.login_central_utils.login_central_read_queries import get_by_user_name, get_by_user_id
from db.crud_utils.login_central_utils.login_central_service import signup_user
from db.crud_utils.login_central_utils.login_central_write_queries import save_new_user, save_prev_user
from db.crud_utils.permission_utils.permission_write import dbsave_user_permission
from db.crud_utils.sub_account_utils.sub_account_write import save_sub_accounts
from db.crud_utils.sub_account_utils.sub_accounts_read import get_total_sub_accounts, get_sub_account
from db.models.permission import permission
from db.models.sub_accounts import sub_accounts


async def creating_new_user(user, mail, name):
    try:
        if user.parent_mail != None:
            return {"data": f"Can not create accounts from sub account.", "error": True}
        if user.demo_expiry < datetime.datetime.now():
            return {"data": f"Account expired, Can not create sub account.", "error": True}
        if not user.paid:
            return {"data": f"Please make payment before adding child/slave user.", "error": True}
        if name == "":
            return {"data": f"Name is required", "error": True}
        accounts_info = await get_total_sub_accounts(user.id)
        by_subaccount = False
        if mail == "":
            if len(accounts_info) > 0:
                mail = str(len(accounts_info) + 1) + "_" + user.user_name
            else:
                mail = "1_" + user.user_name
            by_subaccount = True
        if name == "":
            name = mail.split('@')[0]
        signup_res = await signup_user(mail, ''.join(random.choices(string.ascii_letters + string.digits, k=7)), user.phone_no, user.source, user.my_referral_code, by_subaccount=by_subaccount,parent_mail=user.user_name)
        if signup_res['error']:
            return signup_res
        sa = sub_accounts()
        sa.main_user_id = user.id
        sa.mail = mail
        sa.name = name
        await save_sub_accounts(sa)
        new_user = await get_by_user_name(mail)
        prev_data = permission()
        prev_data.master_account = user.id
        prev_data.slave_account = new_user.id
        # if by_subaccount == False:
        #     prev_data.active = True
        #     await send_email(mail, subject="Action Required: Account Management Request Received", username="",
        #                      msg_data=mail, mail_type='admin_permission_request',
        #                      user_data_dict={'demo': False, 'user_name': mail})
        # else:
        prev_data.active = True
        prev_data.request_token = uuid.uuid4()
        prev_data.request_created = datetime.datetime.now()
        prev_data.request_accepted = None
        await dbsave_user_permission(prev_data)

        return {"data": signup_res['data'], "error": False}
    except Exception as e:
        logger.error(f"error in creating_new_user {traceback.format_exc()}")
        return {"data": f"Error creating users {e}", "error": True}


async def getting_accounts(user):
    try:
        res = []
        accounts_info = await get_total_sub_accounts(user.id)
        if accounts_info == 0:
            account = await get_sub_account(user.user_name)
            main_user = await get_by_user_id(account.main_user_id)
            accounts_info = await get_total_sub_accounts(account.main_user_id)
            res.append({"name": 'master_account', "mail": main_user.user_name, "expiry": str(main_user.demo_expiry),
                        "token": main_user.random_id, "session": main_user.authtoken})

        for ai in accounts_info:
            u = await get_by_user_name(ai.mail)
            if u == None:
                logger.error(f"user mail not found for getting sub account {ai.mail}")
                continue
            id = u.random_id
            exp = str(u.demo_expiry)
            token = generate_salted_hash(ai.mail + "" + str(datetime.datetime.now()))
            u.authtoken = token
            await save_prev_user(u)
            res.append({"name":ai.name,"mail":ai.mail,"expiry":exp,"token":id,"session":token})

        return {"data": res, "error": False}
    except Exception as e:
        logger.error(f"error in getting_accounts {traceback.format_exc()}")
        return {"data": f"Error creating users {e}", "error": True}
