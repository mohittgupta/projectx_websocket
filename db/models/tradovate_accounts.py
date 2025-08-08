
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class tradovate_accounts(Base):
    __tablename__ = 'tradovate_accounts'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_random_id = Column(String())
    tradovate_account_name = Column(String())
    tradovate_account_id = Column(String())
    engine = Column(String())
    active = Column(Boolean())
