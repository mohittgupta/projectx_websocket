from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime
from sqlalchemy import Column, Integer, ForeignKey

# position["side"].upper() == opposite_side and position["tradableInstrumentId"] == str(instrument_id):
#                 close_quantity = float(position["qty"]) if reverse else min(float(position["qty"]), new_quantity)

class trade_locker_positions(Base):
    __tablename__ = 'trade_locker_positions'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('login_central.id', ondelete="CASCADE"), nullable=False)
    position_id = Column(String())
    side = Column(String())
    tradable_instrument_id = Column(String())
    quantity = Column(Float())
    active = Column(Boolean(), default=True)