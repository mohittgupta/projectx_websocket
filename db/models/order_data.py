from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class order_data(Base):
    __tablename__ = 'order_data'
    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    id = Column(String())
    account_id = Column(String())
    demo = Column(Boolean())
    contract_id = Column(String())
    timestamp = Column(String())
    action = Column(String())
    ordStatus = Column(String())
    execution_provider_id = Column(String())
    oco_id = Column(String())
    parent_id = Column(String())
    archived = Column(Boolean())
    external = Column(Boolean())
    admin = Column(Boolean())
    order_date = Column(DateTime())
    user_id = Column(String())

    symbol = Column(String())
    order_type = Column(String())
    quantity = Column(String())

    table_id = Column(String())
    table_side = Column(String())

    price = Column(String())
    avgprice = Column(String())
    order_msg = Column(String())

    account = Column(String())
    platform = Column(String())
    connection_name = Column(String())