import traceback

from sqlalchemy import and_

from config import logger
from db.models.contract_info import contract_info
from db.database import db_session

def get_by_name_contract_info(name):
    try:
        entity = db_session.query(contract_info).filter(contract_info.name == str(name)).first()
        db_session.close()
        return entity
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
    return None
