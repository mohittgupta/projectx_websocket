from sqlalchemy import and_

from db.models.order_data import order_data
from db.database import db_session

def get_by_order_id_by_user_id(user_id):
    entity = db_session.query(order_data).filter(order_data.user_id == user_id).all()
    db_session.close()
    return entity

def get_by_order_id_order_details_desc(id):
    entity = db_session.query(order_data).filter(order_data.id == id).order_by(order_data.row_id.desc()).first()
    db_session.close()
    return entity

def get_by_order_id_order_details(id,timestamp):
    entity = db_session.query(order_data).filter(order_data.id == id).filter(order_data.timestamp == timestamp).first()
    db_session.close()
    return entity

def get_by_date_order_details(user,from_date,to_date, engine):

    entity = db_session.query(order_data).filter(order_data.platform == engine).filter(order_data.user_id == user.random_id).filter(order_data.order_date >= from_date).filter(order_data.order_date < to_date).all()
    db_session.close()
    return entity