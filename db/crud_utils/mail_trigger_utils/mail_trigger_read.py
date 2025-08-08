import traceback

from config import logger
from db.database import db_session
from db.models.mail_trigger import mail_trigger


async def get_triggers_by_user_id(id):
    try:
        user = db_session.query(mail_trigger).filter(mail_trigger.user_id == id).first()
        db_session.close()
        return user
    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None