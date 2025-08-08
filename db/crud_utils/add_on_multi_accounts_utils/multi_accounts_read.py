# import logging
# import traceback
#
# from sqlalchemy import and_, or_
#
# from config import logger
# from db.models.accounts_add_on import accounts_add_on
# from db.database import db_session
#
# def get_add_on_account_by(user_id):
#     try:
#         user = db_session.query(accounts_add_on).filter(accounts_add_on.user == user_id).all()
#         db_session.close()
#         return user
#     except Exception as e:
#         logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
#         db_session.rollback()
#         db_session.close()
#         return []
# def get_add_on_by_id(id):
#     try:
#         user = db_session.query(accounts_add_on).filter(accounts_add_on.id == id).first()
#         db_session.close()
#         return user
#     except Exception as e:
#         logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
#         db_session.rollback()
#         db_session.close()
#         return None