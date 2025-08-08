import datetime
import json
import random
import string
import traceback
from dataclasses import asdict
from typing import Any

from business_logic.encode_decode import generate_salted_hash
from db.crud_utils.login_central_utils.login_central_read_queries import get_by_user_id
from db.crud_utils.login_central_utils.login_central_redis_dto_converter import convert_login_cen_into_dto
from db.crud_utils.user_proxy_utils.user_proxy_write import saving_user_proxy
from db.dtos.UserDto import UserDto
from db.models.login_central import login_central
from db.crud_utils.login_central_utils.login_central_read_queries import *
from db.database import db_session
from config import default_user, default_password, free_multi_account, logger, login_central_redis
from db.models.user_proxy import user_proxy


# def add_default_user():
#     login_user = get_by_user_name(default_user)
#     if login_user == None:
#         entity = login_central()
#         entity.user_name = default_user
#         entity.password = default_password
#         db_session.add(entity)
#         db_session.commit()
#         db_session.close()

async def save_new_user(user,password,password_hash, random_key,referral_id , phone_no,source,other_user_referral_code):
    verification_key = generate_salted_hash(user + "" + str(datetime.datetime.now()))
    entity = login_central()
    entity.user_name = user
    entity.password = password
    entity.password_hash = password_hash
    entity.random_id = random_key

    entity.my_referral_code = referral_id
    entity.other_referral_code = ''
    entity.other_user_referral_code = other_user_referral_code
    entity.phone_no = phone_no
    entity.source = source

    entity.mail_verified = False
    entity.mail_verification_token = verification_key

    entity.demo = True
    entity.unsubscribe = False
    entity.pause=False

    entity.profit_goal = 0.0
    entity.loss_goal = 0.0

    entity.demo_expiry = datetime.datetime.now() + datetime.timedelta(days=5)
    entity.paid = False
    entity.created = datetime.datetime.now()
    entity.max_multi_account = free_multi_account
    try:
        db_session.add(entity)
        db_session.commit()
        db_session.close()
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
    return verification_key

# async def save_prev_user(e):
#     try:
#         if type(e) == login_central:
#             if e.id != None and e.id != 0:
#                 userdto = convert_login_cen_into_dto(e)
#             db_session.add(e)
#             db_session.commit()
#             db_session.close()
#         else:
#             #  note saving only specific column value (used in add-trade-data-latest api).
#             logger.info(f"saving data from dict {e.random_id}")
#             dt = await  convert_dto_into_login_central(e)
#             if dt != None:
#                 db_session.add(dt)
#                 db_session.commit()
#                 db_session.close()
#     except Exception as e:
#         logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
#         db_session.rollback()
#         db_session.close()

async def save_prev_user(e):
    try:
        db_session.add(e)
        db_session.commit()
        db_session.close()
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()



async def convert_dto_into_login_central(dto_obj):
    try:
        logger.info(f"getting logcentral data by dto row_id before checking ")
        trade_data_obj = await get_by_user_id(dto_obj.id)
        logger.info(f"getting logcentral data by dto row_id {trade_data_obj} ")
        trade_data_obj.demo_mail_send = dto_obj.demo_mail_send
        trade_data_obj.error_instruction_mail_flag = dto_obj.error_instruction_mail_flag
        trade_data_obj.discount_promotional_flag = dto_obj.discount_promotional_flag
        trade_data_obj.demo_disconnect_flag = dto_obj.demo_disconnect_flag
        trade_data_obj.no_right_trade_flag = dto_obj.no_right_trade_flag
        trade_data_obj.no_trade_flag = dto_obj.no_trade_flag
        trade_data_obj.payment_mail = dto_obj.payment_mail
        trade_data_obj.rollover_mail_send = dto_obj.rollover_mail_send
        return trade_data_obj
    except Exception as e:
        logger.error(f"error in dto converter {traceback.format_exc()}")
    return None
