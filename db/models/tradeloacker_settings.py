
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float


class TradeLockerSetting(Base):
    __tablename__ = 'trade_locker_setting'

    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    random_id = Column(String())
    local_symbol = Column(String())
    inst_type = Column(String())
    order_type = Column(String())
    Exchange = Column(String())
    symbol = Column(String())
    con_id = Column(Integer())
    tradelocker_symbol = Column(String())
    Currency = Column(String())
    lot_size = Column(Float())
    min_tick = Column(Float())
    strike_price_interval = Column(Float())
    MaturityDate = Column(String())
    isin = Column(String())
    quantity = Column(Integer())
    duplicate_position = Column(Boolean())
    cusip = Column(String())
    route = Column(String())
    server = Column(String())