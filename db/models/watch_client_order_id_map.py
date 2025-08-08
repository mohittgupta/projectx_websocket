
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class watch_client_order_id_map(Base):
    __tablename__ = 'watch_client_order_id_map'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    master_token = Column(String())
    child_token = Column(String())
    master_order_id = Column(String())
    child_order_id = Column(String())
    order_type = Column(String())

    master_account_id = Column(String())
    child_account_id = Column(String())
    msg = Column(String())

    datetime = Column(DateTime())