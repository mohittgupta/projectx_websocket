from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class UserBrokers(Base):
    __tablename__ = 'user_brokers'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    broker_id = Column(Integer())
    broker_name = Column(String())
    random_id = Column(String())
    subscription_id = Column(String())
    status = Column(String())