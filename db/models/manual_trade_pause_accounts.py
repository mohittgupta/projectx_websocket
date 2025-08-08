
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class manual_trade_pause_accounts(Base):
    __tablename__ = 'manual_trade_pause_accounts'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer())
    timming_row_id = Column(Integer())
    acc_name = Column(String())
    connection_name = Column(String())