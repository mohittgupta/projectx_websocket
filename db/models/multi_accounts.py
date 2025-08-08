
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class multi_accounts(Base):
    __tablename__ = 'multi_accounts'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_random_id = Column(Integer())
    master_user = Column(String())
    master_account_id = Column(String())
    token = Column(String())
    account_id = Column(String())
    multiplier = Column(Float())
    risk_percentage = Column(Float())

    fixed_quantity = Column(Integer())

    active = Column(Boolean())
    status = Column(Boolean())
    created = Column(DateTime())
