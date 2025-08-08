# from db.database import Base
# from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
#
#
# # position["side"].upper() == opposite_side and position["tradableInstrumentId"] == str(instrument_id):
# #                 close_quantity = float(position["qty"]) if reverse else min(float(position["qty"]), new_quantity)
#
# class trade_locker_positions(Base):
#     __tablename__ = 'trade_locker_positions'
#     id = Column(Integer(), primary_key=True, autoincrement=True)
#     position_id = Column(String())
#     side = Column(String())
#     tradable_instrument_id = Column(String())
#     quantity = Column(Float())

import traceback
from sqlalchemy import and_
from config import logger
from db.database import db_session
from db.models.trade_locker_positions import trade_locker_positions


def get_all_trade_locker_positions():
    try:
        all_trade_locker_positions = db_session.query(trade_locker_positions).all()
        db_session.close()
        return all_trade_locker_positions
    except Exception as e:
        logger.error(f"Exception in get_all_trade_locker_positions: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None

def get_all_trade_locker_positions_by_side_and_instrument_id(user_id, side, instrument_id):
    try:
        all_trade_locker_positions = db_session.query(trade_locker_positions).filter(
            and_(
                trade_locker_positions.user_id == user_id,
                trade_locker_positions.side == str(side).lower(),
                trade_locker_positions.tradable_instrument_id == str(instrument_id),
                trade_locker_positions.active == True
            )
        ).all()
        db_session.close()
        return all_trade_locker_positions
    except Exception as e:
        logger.error(f"Exception in get_all_trade_locker_positions_by_side_and_instrument_id: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None
