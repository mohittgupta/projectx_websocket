from sqlalchemy import and_, or_

from db.models.admin_third_party_access import AdminThirdPartyAccess, AdminUserThirdPartyAccess, AccessType
from db.models.login_central import login_central
from db.database import db_session

def get_by_admin_email(email):
    user = db_session.query(AdminThirdPartyAccess).filter(AdminThirdPartyAccess.admin_email == email).first()
    db_session.close()
    return user

def get_by_admin_user_email(admin_email, user_email):
    user = db_session.query(AdminUserThirdPartyAccess).filter(AdminUserThirdPartyAccess.admin_email == admin_email , AdminUserThirdPartyAccess.user_email == user_email).first()
    db_session.close()
    return user

def get_all_user_by_admin_email(admin_email):
    users = db_session.query(AdminUserThirdPartyAccess).filter(AdminUserThirdPartyAccess.admin_email == admin_email).all()
    db_session.close()
    return users

def get_all_admin_email():
    users = db_session.query(AdminThirdPartyAccess).filter(AdminThirdPartyAccess.access_type == AccessType.MODERATOR ).all()
    db_session.close()
    return users