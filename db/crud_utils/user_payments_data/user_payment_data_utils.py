import traceback

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.orm import Session

from config import logger
from db.models.login_central import login_central
from db.models.user_payment_data import user_payment_data
from db.database import db_session as db_session_def

def get_all_active_user_payments(mail: str, db_session: Session = db_session_def):
    """
    Fetch all active subscriptions for a given email.
    Active subscriptions are determined by status and expiry date.

    Args:
        mail (str): The email address to filter subscriptions.
        db_session (Session): The database session object.

    Returns:
        list: A list of active subscriptions for the given email.
    """
    active_subscriptions = None
    try:
        current_date = datetime.now()
        active_subscriptions = (
            db_session.query(user_payment_data)
            .filter(user_payment_data.email == mail)
            .filter(user_payment_data.expire_by >= current_date)
            .order_by(user_payment_data.id.desc())
            .all()
        )
        db_session.close()
        return active_subscriptions
    except Exception as e:
        logger.info(f"Error : {e}")
    finally:
        db_session.close()
        return active_subscriptions

def get_all_user_payments(mail: str, db_session: Session = db_session_def):
    """
    Fetch all active subscriptions for a given email.
    Active subscriptions are determined by status and expiry date.

    Args:
        mail (str): The email address to filter subscriptions.
        db_session (Session): The database session object.

    Returns:
        list: A list of active subscriptions for the given email.
    """
    active_subscriptions = None
    try:
        current_date = datetime.now()
        active_subscriptions = (
            db_session.query(user_payment_data)
            .filter(user_payment_data.email == mail)
            .order_by(user_payment_data.id.desc())
            .all()
        )
        db_session.close()
        return active_subscriptions
    except Exception as e:
        logger.info(f"Error : {e}")
    finally:
        db_session.close()
        return active_subscriptions

def get_all_latest_user_payments(mail: str, db_session: Session = db_session_def):
    """
    Fetch all active subscriptions for a given email.
    Active subscriptions are determined by status and expiry date.

    Args:
        mail (str): The email address to filter subscriptions.
        db_session (Session): The database session object.

    Returns:
        list: A list of active subscriptions for the given email.
    """
    active_subscriptions = None
    try:
        current_date = datetime.now()
        active_subscriptions = (
            db_session.query(user_payment_data)
            .filter(user_payment_data.email == mail)
            .filter(user_payment_data.expire_by >= current_date)
            .order_by(user_payment_data.id.desc())
            .first()
        )
        db_session.close()
        return active_subscriptions
    except Exception as e:
        logger.info(f"Error : {e}")
    finally:
        db_session.close()
        return active_subscriptions

def get_payment_data(subscription_id, db_session: Session = db_session_def):
    active_subscriptions = None
    try:
        current_date = datetime.now()
        active_subscriptions = (
            db_session.query(user_payment_data)
            .filter(user_payment_data.subscription_id==subscription_id)
            .order_by(user_payment_data.id.desc())
            .first()
        )
    finally:
        db_session.close()
        return active_subscriptions


def add_payment_data(
        subscription_id: str,
        email: str,
        subscription_id_json: str,
        plan_id: str = None,
        status: str = None,
        demo_expiry: datetime = None,
        expire_by: datetime = None,
        db_session: Session = db_session_def
):
    """
    Fetch payment data based on the subscription ID. If found, update the existing payment data.
    If not found, add new payment data.

    Args:
        subscription_id (str): The subscription ID to filter the data.
        email (str): The email address associated with the payment data.
        subscription_id_json (str): JSON string for subscription details.
        plan_id (str): The ID of the plan.
        status (str): The status of the subscription.
        demo_expiry (str): Demo expiry date.
        expire_by (str): Expiry date of the subscription.
        db_session (Session): The database session object.

    Returns:
        user_payment_data: The existing or newly added payment data.
    """
    try:
        # Fetch existing payment data
        payment_data = (
            db_session.query(user_payment_data)
            .filter(user_payment_data.subscription_id == subscription_id)
            .first()
        )

        if payment_data:
            # Update existing payment data
            payment_data.email = email
            payment_data.subscription_id_json = subscription_id_json
            payment_data.plan_id = plan_id
            payment_data.status = status
            payment_data.demo_expiry = demo_expiry
            payment_data.expire_by = expire_by
        else:
            # Add new payment data if not found
            payment_data = user_payment_data(
                email=email,
                subscription_id_json=subscription_id_json,
                subscription_id=subscription_id,
                plan_id=plan_id,
                status=status,
                demo_expiry=demo_expiry,
                expire_by=expire_by
            )
            db_session.add(payment_data)

        db_session.commit()  # Commit changes to the database
        return payment_data.id

    except SQLAlchemyError as e:
        db_session.rollback()  # Rollback any changes in case of an error
        print(f"Database error: {e}")
        return None
    finally:
        db_session.close()


def get_all_active_payments(email , db_session: Session = db_session_def):
    """
    Fetch all active subscriptions.
    Active subscriptions are determined by status and expiry date.

    Args:

        db_session (Session): The database session object.

    Returns:
        list: A list of active subscriptions for the given email.
    """
    active_subscriptions = None
    try:
        current_date = datetime.now()
        active_subscriptions = (
            db_session.query(user_payment_data)
            .filter(user_payment_data.expire_by >= current_date).filter(user_payment_data.email == email)
            .order_by(user_payment_data.id.desc())
            .all()
        )
        db_session.close()
        return active_subscriptions
    finally:
        db_session.close()
        return active_subscriptions


def get_payment_data_by_id(payment_id, db_session: Session = db_session_def):
    entity = db_session.query(user_payment_data).filter(user_payment_data.id == payment_id).first()
    db_session.close()
    return entity

def save_payment_data(e):
    db_session_def.add(e)
    db_session_def.commit()
    db_session_def.close()

def get_all_active_payments_all_users(db_session: Session = db_session_def):
    """
    Fetch all active subscriptions.
    Active subscriptions are determined by status and expiry date.

    Args:

        db_session (Session): The database session object.

    Returns:
        list: A list of active subscriptions for the given email.
    """
    active_subscriptions = None
    try:
        current_date = datetime.now()
        active_subscriptions = (
            db_session.query(user_payment_data)
            .filter(user_payment_data.expire_by >= current_date)
            .order_by(user_payment_data.id.desc())
            .all()
        )
        db_session.close()
        return active_subscriptions
    finally:
        db_session.close()
        return active_subscriptions


def get_payments_all_users(db_session: Session = db_session_def):
    """
    Fetch all active subscriptions.
    Active subscriptions are determined by status and expiry date.

    Args:

        db_session (Session): The database session object.

    Returns:
        list: A list of active subscriptions for the given email.
    """
    active_subscriptions = None
    try:
        current_date = datetime.now()
        active_subscriptions = (
            db_session.query(user_payment_data)
            .filter(user_payment_data.expire_by >= current_date)
            .order_by(user_payment_data.id.desc())
            .all()
        )
        db_session.close()
        return active_subscriptions
    finally:
        db_session.close()
        return active_subscriptions



async def get_users_with_active_subscriptions(db_session: Session = db_session_def):
    """
    Fetch all users from login_central who have active subscriptions.

    Args:
        db_session (Session): The database session object.

    Returns:
        list: A list of users with active subscriptions.
    """
    try:
        current_date = datetime.now()

        # Step 1: Get active subscriptions
        active_subscriptions = (
            db_session.query(user_payment_data)
            .filter(user_payment_data.expire_by >= current_date)
            .order_by(user_payment_data.id.desc())
            .all()
        )

        # Extract emails from active subscriptions
        active_emails = [sub.email for sub in active_subscriptions]

        if not active_emails:
            db_session.close()
            return []

        # Step 2: Get users whose email is in active_emails
        users = (
            db_session.query(login_central)
            .filter(login_central.user_name.in_(active_emails))
            .all()
        )

        db_session.close()
        return users

    except Exception as e:
        logger.error(f"Exception in DB rollback: {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return []

def get_unmapped_payment_or_expired_payment(email,sub_id_string,  db_session: Session = db_session_def):
    """
    Fetch all active subscriptions.
    Active subscriptions are determined by status and expiry date.

    Args:

        db_session (Session): The database session object.

    Returns:
        list: A list of active subscriptions for the given email.
    """
    active_subscriptions = None
    try:
        current_date = datetime.now()
        active_subscriptions = (
            db_session.query(user_payment_data)
            .filter(or_(user_payment_data.expire_by <= current_date, user_payment_data.subscription_id.ilike(f"{sub_id_string}%"))).filter(user_payment_data.email == email)
            .order_by(user_payment_data.id.desc())
            .all()
        )
        db_session.close()
        return active_subscriptions
    finally:
        db_session.close()
        return active_subscriptions