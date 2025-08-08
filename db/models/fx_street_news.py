from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class fx_street_news(Base):
    __tablename__ = 'fx_street_news'
    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    title = Column(String())
    country = Column(String())
    date = Column(String())
    impact = Column(String())
    forecast = Column(String())
    previous = Column(String())
    url = Column(String())

    start_date = Column(DateTime())
