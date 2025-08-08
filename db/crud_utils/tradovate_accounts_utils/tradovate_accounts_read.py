from sqlalchemy import and_

from db.models.tradovate_accounts import tradovate_accounts
from db.database import db_session

def get_tradovate_accounts_by_user_id(user_key , engine):
    entity = db_session.query(tradovate_accounts).filter(tradovate_accounts.engine == engine).filter(tradovate_accounts.user_random_id == user_key).filter(tradovate_accounts.active == True).first()
    db_session.close()
    return entity

def get_tradovate_accounts_by_user_id_name(user_key,account_name):
    entity = (db_session.query(tradovate_accounts).filter(tradovate_accounts.user_random_id == user_key)
              .filter(tradovate_accounts.tradovate_account_name == str(account_name)).first())
    db_session.close()
    return entity




def get_tradovate_accounts_by_id_name(user_key,account_id,account_name):
    entity = db_session.query(tradovate_accounts).filter(tradovate_accounts.user_random_id != user_key).filter(tradovate_accounts.tradovate_account_id == str(account_id)).filter(tradovate_accounts.tradovate_account_name == str(account_name)).all()
    db_session.close()
    return entity


def get_first_tradovate_accounts_by_id_name(account_id,account_name):
    entity = db_session.query(tradovate_accounts).filter(tradovate_accounts.tradovate_account_id == str(account_id)).filter(tradovate_accounts.tradovate_account_name == str(account_name)).first()
    db_session.close()
    return entity



def get_tradovate_accounts_by_userid(user_id):
    entity = db_session.query(tradovate_accounts).filter(tradovate_accounts.user_random_id == str(user_id)).all()
    db_session.close()
    return entity