from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class news_symbol_mapping(Base):
    __tablename__ = 'news_symbol_mapping'
    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    tradovate_root_symbol = Column(String())
    news_symbol = Column(String())
    country = Column(String())