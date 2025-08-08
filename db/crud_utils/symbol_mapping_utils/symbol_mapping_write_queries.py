from db.database import db_session


def add_symbol_mapping(data):
    db_session.add(data)
    db_session.commit()
    db_session.close()
