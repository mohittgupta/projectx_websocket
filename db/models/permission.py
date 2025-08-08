from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,DateTime,Float

class permission(Base):
    __tablename__ = 'permission'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    master_account = Column(Integer())
    slave_account = Column(Integer())
    active = Column(Boolean())
    request_token = Column(String())
    request_created = Column(DateTime())
    request_accepted = Column(DateTime())