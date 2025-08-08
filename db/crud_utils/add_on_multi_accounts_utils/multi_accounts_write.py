# import traceback
#
# from config import logger
# from db.database import db_session
#
# def save_add_on_client(e):
#     try:
#         db_session.add(e)
#         db_session.commit()
#         db_session.close()
#     except Exception as e:
#         logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
#         db_session.rollback()
#         db_session.close()
#
# def del_add_on_client(e):
#     try:
#         db_session.delete(e)
#         db_session.commit()
#         db_session.close()
#     except Exception as e:
#         logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
#         db_session.rollback()
#         db_session.close()
