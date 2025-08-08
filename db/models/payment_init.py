from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class payment_init(Base):
    __tablename__ = 'payment_init'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    subscription_id = Column(String())
    amount = Column(Float())
    real_amount = Column(Float())
    amount_paid = Column(Float())
    amount_due = Column(Float())
    order_id = Column(String())
    currency = Column(String())
    user_mail = Column(String())
    receipt_id = Column(String())
    created_at = Column(String())
    status = Column(String())
    server_created_time = Column(DateTime())
    server_updated_time = Column(DateTime())
    payment_id = Column(String())