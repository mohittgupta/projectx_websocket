import traceback

from config import logger
from db.crud_utils.tradovate_accounts_utils.tradovate_accounts_read import get_tradovate_accounts_by_user_id_name
from db.crud_utils.tradovate_accounts_utils.tradovate_accounts_write import save_tradovate_accounts
from db.models.tradovate_accounts import tradovate_accounts


async def add_tradovate_accounts(user_key,account_id,account_name , engine):
    try:
        logger.info(f"Saving..... tr {account_id}")
        prev_data = get_tradovate_accounts_by_user_id_name(user_key,account_name)
        if prev_data == None:
            ta = tradovate_accounts()
            ta.tradovate_account_name = str(account_name)
            ta.tradovate_account_id = str(account_id)
            ta.user_random_id = user_key
            ta.engine = engine
            ta.active = True
            await save_tradovate_accounts(ta)
    except Exception as e:
        logger.error(f"error in account saving {traceback.format_exc()}")


async def add_tradovate_accounts_latest(user_key,account_id,account_name, engine):
    try:
        logger.info(f"Saving..... tr latest {account_id}")
        prev_data = get_tradovate_accounts_by_user_id_name(user_key,account_name)
        if prev_data == None:
            ta = tradovate_accounts()
            ta.tradovate_account_name = account_name
            ta.tradovate_account_id = account_id
            ta.user_random_id = user_key
            ta.engine = engine
            ta.active = True
            await save_tradovate_accounts(ta)
    except Exception as e:
        logger.error(f"error in account saving {traceback.format_exc()}")

# todo add permission check...
async def getting_tradovate_tokens(user_key,token,token_user_obj=None):
    try:
        if token == "":
            return {"data":"Invalid token","error":True}

        logger.info(f"getting_tradovate_tokens {token}")
        res = []
        idmap = []
        if token_user_obj == None:
            token_user_obj = await get_by_random_key(token)
        if token_user_obj == None:
            return {"data": "Invalid token", "error": True}
        tradovate_new_accounts = await get_list_account_id(token_user_obj)
        for ta in tradovate_new_accounts:
            if ta == "" or ta == 0:
                continue
            await add_tradovate_accounts_latest(token,str(ta['id']),str(ta['name']))

        prev_data = await get_tradovate_accounts_by_userid(token)
        for p in prev_data:
            if p.tradovate_account_name and p.tradovate_account_name != "":
                res.append(p.tradovate_account_name)
                idmap.append({"name": p.tradovate_account_name, "id":p.tradovate_account_id})
        return {"data": res,"idmap":idmap, "error": False}
    except Exception as e:
        logger.error(f"error in account saving {traceback.format_exc()}")
        return {"data": f"Error {e}","idmap":[], "error": True}
