
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class payment_history(Base):
    __tablename__ = 'payment_history'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer())
    created = Column(DateTime())
    amount = Column(Float())
    subscription_type = Column(String())
    platform = Column(String())
    sub_id = Column(String())

    total_paid = Column(Float())
    total_paid_date = Column(DateTime())
    other_user_referral_code = Column(String())
