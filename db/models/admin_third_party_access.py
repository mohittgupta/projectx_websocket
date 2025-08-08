
from db.database import Base
from sqlalchemy import Column, Integer, String, Enum
import enum

class AccessType(enum.Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"

class AdminThirdPartyAccess( Base):
    __tablename__ = 'admin_third_party_access'

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_email = Column(String)
    access_type = Column(Enum(AccessType), nullable=False)


class AdminUserThirdPartyAccess( Base):
    __tablename__ = 'admin_user_third_party_access'

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_email = Column(String)
    user_email = Column(String)

