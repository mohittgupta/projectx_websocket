from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class rollover_instrument_history(Base):
    __tablename__ = 'rollover_instrument_history'
    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    root_symbol = Column(String())
    old_contract = Column(String())
    new_cotract = Column(String())
    old_contract_exp = Column(String())
    new_cotract_exp = Column(String())