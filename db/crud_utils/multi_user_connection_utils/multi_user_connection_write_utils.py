from db.database import db_session
from db.models.multi_user_connections import MultiUserConnections


def create_multi_user_connection(user_id,user_broker_id, user_payment_id, user_random_id, connection_name, engine,connection_environment=None,
                                 connection_username=None, connection_password=None,
                                 connection_account_number=None, connection_server=None, active=None):
    entity = MultiUserConnections(
        user_id=user_id,
        user_broker_id=user_broker_id,
        user_payment_id=user_payment_id,
        user_random_id=user_random_id,
        connection_name=connection_name,
        engine=engine,
        connection_environment=connection_environment,
        connection_username=connection_username,
        connection_password=connection_password,
        connection_account_number=connection_account_number,
        connection_server=connection_server,
        active=active
    )
    db_session.add(entity)
    db_session.commit()
    db_session.close()
    return entity


def update_multi_user_connection(id, **kwargs):
    entity = db_session.query(MultiUserConnections).filter(MultiUserConnections.id == id).first()
    if entity:
        # Ensure mandatory fields are not removed if updated
        mandatory_fields = ["user_id", "user_payment_id", "user_random_id", "connection_name", "engine"]
        for field in mandatory_fields:
            if field in kwargs and kwargs[field] is None:
                raise ValueError(f"{field} cannot be set to None")

        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        db_session.commit()
        db_session.refresh(entity)
    db_session.close()
    return entity


def delete_multi_user_connection(id):
    entity = db_session.query(MultiUserConnections).filter(MultiUserConnections.id == id).first()
    if entity:
        db_session.delete(entity)
        db_session.commit()
    db_session.close()
    return entity is not None

def save_connection_data(e):
    db_session.add(e)
    db_session.commit()
    db_session.close()
