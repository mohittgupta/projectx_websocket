from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class Brokers(Base):
    __tablename__ = 'brokers'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    broker_id = Column(Integer() , unique=True)
    broker_name = Column(String(), unique=True)