
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,DateTime,Float

class subscription_refund(Base):
    __tablename__ = 'subscription_refund'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer())
    amount = Column(Float())
    created = Column(DateTime())