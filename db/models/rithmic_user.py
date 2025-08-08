
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,DateTime,Float

class rithmic_user(Base):
    __tablename__ = 'rithmic_user'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(String())
    user_name = Column(String())
    password = Column(String())
    system_name = Column(String())
    created = Column(DateTime())
    connected = Column(Boolean())
    active = Column(Boolean())
