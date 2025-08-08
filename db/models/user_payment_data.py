from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class user_payment_data(Base):
    __tablename__ = 'user_payment_data'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    email = Column(String(750), nullable=False)
    subscription_id_json = Column(String(),nullable=False)
    subscription_id = Column(String(),nullable=False)
    plan_id = Column(String())
    status = Column(String())
    demo_expiry = Column(DateTime())
    expire_by = Column(DateTime())