import datetime
import random
import string

from business_logic.encode_decode import generate_salted_hash
from config import app_obj
from db.crud_utils.login_central_utils.login_central_read_queries import get_by_auth_key, get_by_admin_key, \
    get_by_exe_key
from db.crud_utils.login_central_utils.login_central_write_queries import save_prev_user


def set_access_token(random_key):
    token = ''
    while True:
        token = generate_salted_hash('t'.join(random.choices(string.ascii_uppercase + string.digits, k=10))+""+str(datetime.datetime.now()))
        if app_obj.get("app").config.token.get(token) == None:break
    app_obj.get("app").config.token.update({ token:random_key})
    return token

def get_user_key_from_token(token):
    if app_obj.get("app").config.token.get(token) == None:
        return None
    else:
        return app_obj.get("app").config.token.get(token)

async def remove_access_token(token):
    try:
        token = token.split('Bearer')[1].strip() if token != None else token
        if token != None:
            user = get_by_auth_key(token)
            if user != None:
                user.authtoken = ''
                await save_prev_user(user)

        # if app_obj.get("app").config.token.get(token) != None:
        #     del app_obj.get("app").config.token[token]
    except Exception as e:
        pass


def access_token_check(token):
    if token == None:
        return None
    if len(token.split('Bearer')) == 0:
        return None
    token = token.split('Bearer')[1].strip() if token != None else token
    if token == None:
        return None
    user = get_by_auth_key(token)
    return user
    # if token == None or app_obj.get("app").config.token.get(token) == None:
    #     return None
    # else:
    #     return app_obj.get("app").config.token.get(token)

def exe_token_check(token):
    if token == None:
        return None
    if len(token.split('Bearer')) == 0:
        return None
    token = token.split('Bearer')[1].strip() if token != None else token
    if token == None:
        return None
    user = get_by_exe_key(token)
    return user
    # if token == None or app_obj.get("app").config.token.get(token) == None:
    #     return None
    # else:
    #     return app_obj.get("app").config.token.get(token)

def admin_access_token_check(token):
    if token == None:
        return None
    if len(token.split('Bearer')) == 0:
        return None
    token = token.split('Bearer')[1].strip() if token != None else token
    if token == None:
        return None
    user = get_by_admin_key(token)
    return user