
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class trade_max_retry_check(Base):
    __tablename__ = 'trade_max_retry_check'
    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(String())
    prev_date_time = Column(DateTime())
    max_trade = Column(Integer())
