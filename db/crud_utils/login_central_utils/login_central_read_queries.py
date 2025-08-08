import json
import logging
import traceback

from sqlalchemy import and_, or_

from config import logger, login_central_redis
from db.crud_utils.login_central_utils.login_central_redis_dto_converter import convert_login_cen_into_dto, convert_dict_into_dto

from db.dtos.UserDto import  UserDto
from db.models.login_central import login_central
from db.database import db_session


async def get_users_which_have_Refrel():
    try:
        user = db_session.query(login_central).filter(login_central.other_user_referral_code != None).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_by_mail_token(token):
    try:
        user = db_session.query(login_central).filter(login_central.mail_verification_token == token).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None
async def get_by_user_main_key(random_id):
    try:
        user = db_session.query(login_central).filter(login_central.random_id == random_id).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_by_user_name(user_name):
    try:
        user = db_session.query(login_central).filter(login_central.user_name == user_name).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_by_account_not_verified():
    try:
        user = db_session.query(login_central).filter(login_central.mail_verified != True).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_by_users_name(user_name):
    try:
        user = db_session.query(login_central).filter(login_central.user_name == user_name).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []
async def get_by_reset_link(code):
    try:
        user = db_session.query(login_central).filter(login_central.reset_link == code).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def getting_login_data_from_redis(random_key):
    try:
        return login_central_redis.get(random_key)
    except Exception as e:
        logger.error(f"error in redis connection {traceback.format_exc()}")
    return None

async def get_by_random_key_for_trade(random_key):
    try:
        logger.info(f"getting user")
        data = getting_login_data_from_redis(random_key)
        if data == None:
            user = db_session.query(login_central).filter(login_central.random_id == random_key).first()
            logger.info(f"getting user DONE")
            db_session.close()
            logger.info(f"close user DONE")
            if user != None:
                userdto = convert_login_cen_into_dto(user)
            return user
        else:
            logger.info(f"getting from redis... ")
            d = convert_dict_into_dto(json.loads(data))
            if d == None:
                user = db_session.query(login_central).filter(login_central.random_id == random_key).first()
                logger.info(f"from redis getting user DONE")
                db_session.close()
                logger.info(f"close user DONE")
                return user
            return d
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None
async def get_by_random_key(random_key):
    try:
        logger.info(f"getting user")
        # result = db_session.execute("SELECT * FROM login_central WHERE random_id='3tBtKt1tWtStNtPtUt9tQt4tA';")
        # user = result.fetchone()
        user = db_session.query(login_central).filter(login_central.random_id == random_key).first()
        logger.info(f"getting user DONE")
        db_session.close()
        logger.info(f"close user DONE")
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def get_by_referral_id(referral_id):
    try:
        user = db_session.query(login_central).filter(login_central.my_referral_code == referral_id).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

async def user_connected_users(referral_id):
    try:
        user = db_session.query(login_central).filter(login_central.other_user_referral_code == referral_id).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

def get_by_auth_key(token):
    try:
        user = db_session.query(login_central).filter(login_central.authtoken == token).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None
async def get_by_user_name_password(user_name,password):
    try:
        user = db_session.query(login_central).filter(login_central.user_name == user_name).filter(login_central.password == password).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_by_user_id(user_id):
    try:
        user = db_session.query(login_central).filter(login_central.id == user_id).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None
async def get_by_demo_from_to_date(from_date,to_date):
    try:
        user = db_session.query(login_central).filter(and_(login_central.demo_expiry >= from_date.date(),login_central.demo_expiry <= to_date.date())).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []
async def get_all_users():
    try:
        user = db_session.query(login_central).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_all_users_for_renew_token():
    try:
        user = db_session.query(login_central).filter(or_(login_central.demo_token_exp != None,login_central.live_token_exp != None)).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

async def get_by_demo_not_expired(from_date):
    try:
        user = db_session.query(login_central).filter(login_central.demo_expiry >= from_date.date()).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []
async def get_by_demo_expired(from_date):
    try:
        user = db_session.query(login_central).filter(login_central.demo_expiry < from_date.date()).filter(or_(login_central.demo_token_exp != None,login_central.live_token_exp != None)).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

def get_by_user_email(user_name):
    user = db_session.query(login_central).filter(login_central.user_name == user_name).first()
    db_session.close()
    return user

def get_by_exe_key(token):
    user = db_session.query(login_central).filter(login_central.exetoken == token).first()
    db_session.close()
    return user

def get_by_admin_key(token):
    user = db_session.query(login_central).filter(login_central.admin_token == token).first()
    db_session.close()
    return user

async def get_by_user_id_from_to(from_id,to_id):
    try:
        user = db_session.query(login_central).filter(and_(login_central.id >= from_id , login_central.id < to_id)).all()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []