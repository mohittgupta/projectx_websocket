from datetime import datetime

from sqlalchemy import or_

from db.database import db_session
from db.models.multi_user_connections import MultiUserConnections
from db.models.user_payment_data import user_payment_data
from utils.linetimer import timing_decorator


def get_multi_user_connection_by_id(id):
    entity = db_session.query(MultiUserConnections).filter(MultiUserConnections.id == id).first()
    db_session.close()
    return entity


def get_multi_user_connections_by_user_id(user_id):
    entities = db_session.query(MultiUserConnections).filter(MultiUserConnections.user_id == user_id).all()
    db_session.close()
    return entities

def get_multi_user_connections_by_id_and_sub_id(user_id, user_payment_id):
    entity = db_session.query(MultiUserConnections).filter(MultiUserConnections.user_payment_id == user_payment_id , MultiUserConnections.user_id==user_id).first()
    db_session.close()
    return entity

def get_active_multi_user_connections():
    entities = db_session.query(MultiUserConnections).filter(MultiUserConnections.active == True).all()
    db_session.close()
    return entities


def get_first_active_multi_user_connection(user_id):
    entity = db_session.query(MultiUserConnections).filter(
        MultiUserConnections.user_id == user_id,
        MultiUserConnections.active == True
    ).first()
    db_session.close()
    return entity

def get_multi_user_connections_by_payment_id(payment_id):
    entities = db_session.query(MultiUserConnections).filter(MultiUserConnections.user_payment_id == payment_id).all()
    db_session.close()
    return entities


def get_multi_user_connections_by_username_or_server(username, server):
    entities = db_session.query(MultiUserConnections).filter(
        or_(
            MultiUserConnections.connection_username == username,
            MultiUserConnections.connection_server == server
        )
    ).all()
    db_session.close()
    return entities


def get_multi_user_connections_by_user_id_and_engine(user_id, engine):
    entities = db_session.query(MultiUserConnections).filter(
        MultiUserConnections.user_id == user_id,
        MultiUserConnections.engine == engine
    ).all()
    db_session.close()
    return entities

def get_multi_user_connections_by_connection_name(user_id,connection_name) -> MultiUserConnections:
    entity = db_session.query(MultiUserConnections).filter(MultiUserConnections.user_id == user_id, MultiUserConnections.connection_name == connection_name).first()
    db_session.close()
    return entity


def get_multi_user_connections_brokers_by_id(user_id, id):
    entity = db_session.query(MultiUserConnections).filter(MultiUserConnections.user_broker_id == id, MultiUserConnections.user_id == user_id).all()
    db_session.close()
    return entity

#
# def get_all_user_brokers_by_subscription():
#     today = datetime.utcnow()
#
#     entity = db_session.query(UserBrokers).join(
#         user_payment_data, UserBrokers.subscription_id == user_payment_data.subscription_id
#     ).filter(
#         user_payment_data.expire_by >= today
#     ).all()
#
#     db_session.close()
#     return entity


def get_all_inactive_connnection_for_broker(user_id, broker_id):

    entity = db_session.query(MultiUserConnections).filter(
        MultiUserConnections.user_id == user_id,
        MultiUserConnections.user_broker_id == broker_id,
        MultiUserConnections.active == False,
        MultiUserConnections.user_payment_id !=-100,
    ).all()

    db_session.close()
    return entity

def get_no_payment_connnection_for_broker(user_id, broker_id):

    entity = db_session.query(MultiUserConnections).filter(
        MultiUserConnections.user_id == user_id,
        MultiUserConnections.user_broker_id == broker_id,
        MultiUserConnections.user_payment_id == -100,
    ).first()

    db_session.close()
    return entity

def get_all_active_connnection_for_broker(user_id, engine):

    entity = db_session.query(MultiUserConnections).filter(
        MultiUserConnections.user_id == user_id,
        MultiUserConnections.engine == engine,
        MultiUserConnections.active == True
    ).all()

    db_session.close()
    return entity

def get_all_user_payment_data_not_mapped(email):
    current_date = datetime.now()
    entity = (
        db_session.query(user_payment_data)
        .outerjoin(MultiUserConnections, user_payment_data.id == MultiUserConnections.user_payment_id)
        .filter(MultiUserConnections.user_payment_id.is_(None))
        .filter(user_payment_data.email == email)
        .filter(user_payment_data.expire_by >= current_date)
        .all()
    )
    db_session.close()
    return entity

def user_multi_connection_with_payment_expired(user_id, engine):
    current_date = datetime.now()
    entity = (
        db_session.query(MultiUserConnections)
        .outerjoin(user_payment_data, MultiUserConnections.user_payment_id == user_payment_data.id)
        .filter(MultiUserConnections.user_id == user_id)
        .filter(user_payment_data.expire_by < current_date)
        .filter(MultiUserConnections.engine == engine)
        .first()
    )
    db_session.close()
    return entity

def get_multi_user_by_engine(engine):
    entities = db_session.query(MultiUserConnections).filter(
        MultiUserConnections.engine == engine
    ).all()
    db_session.close()
    return entities

def get_multi_user_by_engine_and_user_id_connection_username(engine, user_id , connection_user_name):
    entities = db_session.query(MultiUserConnections).filter(
        MultiUserConnections.engine == engine,
        MultiUserConnections.user_id == user_id,
        MultiUserConnections.connection_username == connection_user_name
    ).first()
    db_session.close()
    return entities

def get_multi_user_by_payment_id(user_id, payment_id):
    entity = db_session.query(MultiUserConnections).filter(
        MultiUserConnections.user_payment_id == payment_id,
        MultiUserConnections.user_id == user_id
    ).first()
    db_session.close()
    return entity


def get_demo_connection_or_expired_connection(session : db_session, user_id: int):
    result = session.query(MultiUserConnections).join(
        user_payment_data, MultiUserConnections.user_payment_id == user_payment_data.id
    ).filter(
        MultiUserConnections.user_id == user_id,
        or_(
            user_payment_data.subscription_id.like('demo%'),
            user_payment_data.expire_by < datetime.utcnow()
        )
    ).first()
    db_session.close()
    return result

def get_multi_user_engine_and_user_id(engine, user_id):
    entity = db_session.query(MultiUserConnections).filter(
        MultiUserConnections.engine == engine,
        MultiUserConnections.user_id == user_id
    ).all()
    db_session.close()
    return entity

def get_multi_user_connection_by_subscription_id(subscription_id):
    entity = (
        db_session.query(MultiUserConnections)
        .outerjoin(user_payment_data, user_payment_data.id == MultiUserConnections.user_payment_id)
        .filter(user_payment_data.subscription_id == subscription_id)

        .first()
    )
    db_session.close()
    return entity

def get_all_no_payment_connnection_for_broker(user_id, broker_id):

    entity = db_session.query(MultiUserConnections).filter(
        MultiUserConnections.user_id == user_id,
        MultiUserConnections.user_broker_id == broker_id,
        MultiUserConnections.user_payment_id == -100,
    ).all()

    db_session.close()
    return entity