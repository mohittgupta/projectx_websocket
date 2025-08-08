import traceback


from sqlalchemy import and_,select

from config import on_off_async_db, logger, user_proxy_obj
from db.models.user_proxy import user_proxy
from db.database import db_session

async def get_user_assigned_ip(user_id):
    if user_proxy_obj.get(user_id) == None:
        entity = db_session.query(user_proxy).filter(user_proxy.user_id == user_id).first()
        db_session.close()
        if entity != None and entity.ip != None and entity.ip != "":
            complete_use = "yes"
            if entity.complete_use == None or entity.complete_use == False:
                complete_use = "no"
                #  this is only for websocket
                return {"ip": entity.ip, "port": entity.port}
            else:
                user_proxy_obj.update({user_id: {"ip": entity.ip, "port": entity.port, "complete_use": complete_use}})


    return user_proxy_obj.get(user_id)