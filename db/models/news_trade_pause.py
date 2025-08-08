from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class news_trade_pause(Base):
    __tablename__ = 'news_trade_pause'
    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(String())
    stop_before_in_minute = Column(Integer())
    start_after_in_minute = Column(String())
    closed_position_open_order = Column(Boolean())
