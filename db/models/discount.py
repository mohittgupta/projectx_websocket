
from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,DateTime,Float

class discount(Base):
    __tablename__ = 'discount'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    code = Column(String())
    discount = Column(Float())
    monthly_product_id = Column(String())
    yearly_product_id = Column(String())
    quarterly_product_id = Column(String())

    monthly_plan_id = Column(String())
    yearly_plan_id = Column(String())
    quarterly_plan_id = Column(String())

    monthly_amount = Column(Float())
    yearly_amount = Column(Float())
    quarterly_amount = Column(String())

    paddel_monthly_plan_id = Column(String())
    paddel_yearly_plan_id = Column(String())
    paddel_quarterly_plan_id = Column(String())

    expired = Column(DateTime())
    active = Column(Boolean())
