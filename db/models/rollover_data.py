from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class rollover_data(Base):
    __tablename__ = 'rollover_data'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    root_symbol = Column(String())
    exchange = Column(String())
    contract_maturity_id = Column(String())
    contract_id = Column(String())
    name = Column(String())
    tick = Column(String())
    expiry = Column(DateTime())
    expiry_id = Column(String())
    expiry_product_id = Column(String())