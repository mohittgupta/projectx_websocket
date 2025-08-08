
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class contract_info(Base):
    __tablename__ = 'contract_info'
    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String())
    id = Column(Integer())
    product_type = Column(String())
    description = Column(String())
    lot_size = Column(Float())
    min_tick = Column(Float())
    price_format = Column(Float())
    exchange_id = Column(Integer())
    status = Column(String())