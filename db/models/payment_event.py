from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime,JSON

class payment_event(Base):
    __tablename__ = 'payment_event'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    event = Column(JSON())
    payment_id = Column(String())
    event_datetime = Column(DateTime())