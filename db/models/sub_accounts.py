from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,DateTime,Float

class sub_accounts(Base):
    __tablename__ = 'sub_accounts'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    main_user_id = Column(Integer())
    name = Column(String())
    mail = Column(String())
