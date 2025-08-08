
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,DateTime,Float

class robinhood_access_token(Base):
    __tablename__ = 'robinhood_access_token'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_random_id = Column(String())
    access_token = Column(String())
    token_type = Column(String())
    device_token = Column(String())
    backup_code = Column(String())
    refresh_token = Column(String())
    mfa_code = Column(String())
    expired = Column(DateTime())

    rb_user_name = Column(String())
    rb_password = Column(String())
    rb_totp = Column(String())

