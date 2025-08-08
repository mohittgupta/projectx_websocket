from sqlalchemy import Column, Integer, String, UniqueConstraint

from db.database import Base


class IBMetaData(Base):
    __tablename__ = 'ib_meta_data'

    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    symbol = Column(String())
    maturity_date = Column(String())
    trading_class = Column(String())
    inst_type = Column(String())

    # Enforce unique constraint on symbol, maturity_date, trading_class, and inst_type
    __table_args__ = (UniqueConstraint('symbol', 'maturity_date', 'trading_class', 'inst_type', name='uq_ib_metadata'),)
