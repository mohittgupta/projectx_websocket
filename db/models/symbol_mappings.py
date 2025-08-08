from datetime import  datetime
from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime


class SymbolMapping(Base):
    __tablename__ = 'symbol_mappings'
    id = Column(Integer, primary_key=True)
    tradestation_symbol = Column(String(50))
    tradingview_symbol = Column(String(50))
    instrument_type = Column(String(20))
    source = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
