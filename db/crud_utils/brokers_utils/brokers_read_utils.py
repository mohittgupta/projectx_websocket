from sqlalchemy import or_
from db.database import db_session
import re
from db.models.brokers import Brokers


def get_all_brokers():
    entity = db_session.query(Brokers).all()
    db_session.close()
    return entity

def get_brokers_by_id(id):
    entity = db_session.query(Brokers).filter(Brokers.broker_id == id).first()
    db_session.close()
    return entity