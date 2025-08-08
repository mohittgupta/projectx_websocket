from config import SQLALCHEMY_SECRET
from db.database import Base
from sqlalchemy import Column, Integer, ForeignKey ,  String,Boolean,DateTime,Float, JSON
from sqlalchemy_utils import StringEncryptedType

class Projectx_Orders(Base):
    __tablename__ = 'projectx_orders'
    # Order update for account 8617480 (code: z0481238fc9a8534dd5943_PROJECTX1_8617480): {'action': 1, 'data': {'id': 1277480053, 'accountId': 8617480, 'contractId': 'CON.F.US.MNQ.U25', 'creationTimestamp': '2025-06-24T07:22:41.1851032+00:00', 'updateTimestamp': '2025-06-24T07:22:41.1851032+00:00', 'status': 1, 'type': 4, 'side': 1, 'size': 1, 'stopPrice': 22305.25, 'fillVolume': 0}
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    connection_name = Column(String, nullable=False)
    order_id = Column(Integer, nullable=False)
    account_id = Column(Integer, nullable=False)
    contract_id = Column(String, nullable=False)
    creation_timestamp = Column(DateTime)
    update_timestamp = Column(DateTime, nullable=True)
    status = Column(Integer)
    type = Column(Integer)
    side = Column(Integer)
    size = Column(Integer)
    fill_volume = Column(Integer, nullable=True)
    price = Column(Float, nullable=True)
    stop_price = Column(Float, nullable=True)
    limit_price = Column(Float, nullable=True)
    fees = Column(Float, nullable=True)
    update_server_time = Column(DateTime, nullable=True)


class Projectx_Trades(Base):
    __tablename__ = 'projectx_trades'
    # Trade update for account 8617480 (code: z0481238fc9a8534dd5943_PROJECTX1_8617480): {'action': 0, 'data': {'id': 1061996295, 'accountId': 8617480, 'contractId': 'CON.F.US.MNQ.U25', 'creationTimestamp': '2025-06-24T07:22:40.2288972+00:00', 'price': 22355.25, 'fees': 0.37, 'side': 0, 'size': 1, 'voided': False, 'orderId': 1277480041}}
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    connection_name = Column(String, nullable=False)
    trade_id = Column(Integer, nullable=False)
    account_id = Column(Integer, nullable=False)
    contract_id = Column(String, nullable=False)
    creation_timestamp = Column(DateTime)
    price = Column(Float)
    fees = Column(Float)
    side = Column(Integer)
    size = Column(Integer)
    voided = Column(Boolean, default=False)
    order_id = Column(Integer)
    update_server_time = Column(DateTime, nullable=True)

class Projectx_Positions(Base):
    __tablename__ = 'projectx_positions'
    # Position update for account 8617480 (code: z0481238fc9a8534dd5943_PROJECTX1_8617480): {'action': 1, 'data': {'id': 287945087, 'accountId': 8617480, 'contractId': 'CON.F.US.MNQ.U25', 'creationTimestamp': '2025-06-24T07:22:40.23633+00:00', 'type': 1, 'size': 1, 'averagePrice': 22355.25}}
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    connection_name = Column(String, nullable=False)
    position_id = Column(Integer, nullable=False)
    account_id = Column(Integer, nullable=False)
    contract_id = Column(String, nullable=False)
    creation_timestamp = Column(DateTime)
    type = Column(Integer)  # Assuming type is an integer
    size = Column(Integer)
    average_price = Column(Float)
    update_server_time = Column(DateTime, nullable=True)
