from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class manual_trade_pause(Base):
    __tablename__ = 'manual_trade_pause'
    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(String())
    start_stop_time = Column(String())
    end_stop_time = Column(String())
    closed_all = Column(Boolean())

