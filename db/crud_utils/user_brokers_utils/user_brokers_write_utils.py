from sqlalchemy import or_
from db.database import db_session
import re
from db.models.brokers import Brokers


def save_user_brokers(entity):
    db_session.add(entity)
    db_session.commit()
    db_session.close()


def delete_user_broker(user_broker):
    try:
        db_session.delete(user_broker)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        print(f"Error deleting user broker: {e}")  # Log or handle the error as necessary
    finally:
        db_session.close()