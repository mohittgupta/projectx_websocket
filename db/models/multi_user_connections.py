from config import SQLALCHEMY_SECRET
from db.database import Base
from sqlalchemy import Column, Integer, ForeignKey ,  String,Boolean,DateTime,Float, JSON
from sqlalchemy_utils import StringEncryptedType

class MultiUserConnections(Base):
    __tablename__ = 'multi_user_connections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('login_central.id', ondelete="CASCADE"), nullable=False)
    user_payment_id = Column(Integer, ForeignKey('user_payment_data.id'), nullable=False)
    user_broker_id = Column(Integer, ForeignKey('brokers.id'), nullable=False)
    user_random_id = Column(String())
    connection_environment = Column(String(), default=None)
    connection_username = Column(String())
    connection_password = Column(StringEncryptedType(String, SQLALCHEMY_SECRET))
    connection_account_number = Column(String())
    connection_account_id = Column(String())
    connection_server = Column(String())
    connection_name = Column(String())
    connection_access_token = Column(String())
    connection_refresh_token = Column(String())
    engine = Column(String())
    active = Column(Boolean() , default=False)
    connection_metadata = Column(JSON())
    connection_datetime = Column(DateTime(), default=None)