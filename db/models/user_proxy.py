from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class user_proxy(Base):
    __tablename__ = 'user_proxy'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer())
    ip = Column(String())
    port = Column(String())
    complete_use = Column(Boolean())