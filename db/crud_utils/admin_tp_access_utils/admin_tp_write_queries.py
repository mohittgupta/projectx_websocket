
from sqlalchemy.exc import SQLAlchemyError

from db.database import db_session
from db.models.admin_third_party_access import AdminThirdPartyAccess, AccessType, AdminUserThirdPartyAccess


async def add_new_admin_access(admin_email, access_type):
    # Create new record
    new_access = AdminThirdPartyAccess(
        admin_email=admin_email,
        access_type=AccessType(access_type)

    )
    try:
        db_session.add(new_access)
        db_session.commit()
        db_session.close()
        return True
    except SQLAlchemyError as e:
        db_session.rollback()
        db_session.close()
        return False

async def add_new_admin_data(admin_email, user_email):
    # Create new record
    new_access = AdminUserThirdPartyAccess(
        admin_email=admin_email,
        user_email=user_email,

    )

    try:
        db_session.add(new_access)
        db_session.commit()
        db_session.close()
        return True
    except SQLAlchemyError as e:
        db_session.rollback()
        db_session.close()
        return False