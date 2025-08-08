from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class accounts_add_on(Base):
    __tablename__ = 'accounts_add_on'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user = Column(Integer())
    client_token = Column(String())
    client_account_id = Column(String())
    active = Column(Boolean())
    updatable = Column(Boolean())
    payment_in = Column(DateTime())
    payment_expiry = Column(DateTime())
    subscription_id = Column(String())
