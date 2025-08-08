from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class robinhood_orders(Base):
    __tablename__ = 'robinhood_orders'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_key = Column(String())

    order_id = Column(String())
    ref_id = Column(String())
    url = Column(String())
    account = Column(String())
    uuid = Column(String())
    position = Column(String())
    cancel = Column(String())
    instrument = Column(String())
    instrument_id = Column(String())
    cumulative_quantity = Column(String())
    average_price = Column(String())
    fees = Column(String())
    price = Column(String())
    stop_price = Column(String())
    quantity = Column(String())
    status = Column(String())
    reject_reason = Column(String())

    created_at = Column(String())
    updated_at = Column(String())
    last_transaction_at = Column(String())
    currency_code = Column(String())
    currency_id = Column(String())
    currency_amount = Column(String())
    order_form_version = Column(String())
    preset_percent_limit = Column(String())
    order_form_type = Column(String())

    order_type = Column(String())
    parent_id = Column(String())
    child_type = Column(String())  # tp,sl
