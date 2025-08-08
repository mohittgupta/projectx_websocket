from xmlrpc.client import boolean

from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime
from sqlalchemy import Column, Integer, ForeignKey

# position["side"].upper() == opposite_side and position["tradableInstrumentId"] == str(instrument_id):
#                 close_quantity = float(position["qty"]) if reverse else min(float(position["qty"]), new_quantity)

class trade_station_orders(Base):
    __tablename__ = 'trade_station_orders'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('login_central.id', ondelete="CASCADE"), nullable=False)
    account_id = Column(String())
    inst_type = Column(String())
    order_id = Column(String())
    symbol = Column(String())
    status = Column(String())
    side = Column(String())

class trade_station_positions(Base):
    __tablename__ = 'trade_station_positions'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('login_central.id', ondelete="CASCADE"), nullable=False)
    account_id = Column(String())
    position_id = Column(String())
    inst_type = Column(String())
    quantity = Column(Float())
    symbol = Column(String())
    status = Column(Boolean() , default=True)
    side = Column(String())