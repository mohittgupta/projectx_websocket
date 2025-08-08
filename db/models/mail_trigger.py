from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class mail_trigger(Base):
    __tablename__ = 'mail_trigger'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer())
    mail_verification_link_send = Column(DateTime())
    account_expired_mail_send = Column(DateTime())