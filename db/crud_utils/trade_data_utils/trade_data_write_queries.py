from db.models.trade_data import trade_data
from db.crud_utils.trade_data_utils.trade_data_read_queries import *
from db.database import db_session



def save_trade_data(data):
    db_session.add(data)
    db_session.commit()
    db_session.close()

def update_orderId_from_row_Id(rowId,entry_orderId):
    db_session.query(trade_data).filter(trade_data.row_id == rowId).update({trade_data.order_id: entry_orderId})
    db_session.commit()
    db_session.close()