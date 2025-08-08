
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class server_start_time(Base):
    __tablename__ = 'server_start_time'
    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    start_time = Column(DateTime())