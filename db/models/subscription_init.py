from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,Float,DateTime

class subscription_init(Base):
    __tablename__ = 'subscription_init'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    subscription_id_json = Column(String())
    subscription_id = Column(String())
    email = Column(String())
    plan_id = Column(String())
    status = Column(String())
    short_url = Column(String())
    amount = Column(String())
    quantity = Column(Integer())
    created_at = Column(String())
    remaining_count = Column(Integer())
    current_end = Column(String())
    expire_by = Column(String())
    server_created_time = Column(DateTime())
    server_updated_time = Column(DateTime())
    mail_send = Column(Boolean())

    platform = Column(String())
    paddle_sub_id = Column(String())
    preminum_done = Column(DateTime())

