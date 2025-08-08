
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class referral_paid(Base):
    __tablename__ = 'referral_paid'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer())
    amount = Column(Float())
    paid_date = Column(DateTime())
    payment_mode = Column(String())