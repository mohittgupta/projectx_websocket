import datetime
import traceback

from config import logger
from db.crud_utils.payment_history_utils.payment_history_write import add_payment_history
from db.models.payment_history import payment_history


async def saving_payment_history(user_id,subs_type,platform,amount,subscription_id,other_user_referral_code,created=datetime.datetime.now()):
    try:
        logger.info(f"we are saving one on one payment history for user {user_id} refrell code is {other_user_referral_code}  subs_type {subs_type} platform {platform} amount {amount} , subscription_id {subscription_id}")
        ph = payment_history()
        ph.user_id = user_id
        ph.created = created
        ph.amount = float(amount) if amount != None and amount != "" else 0
        ph.subscription_type = subs_type
        ph.platform = platform
        ph.sub_id = subscription_id
        ph.total_paid = 0
        ph.other_user_referral_code = other_user_referral_code
        await add_payment_history(ph)
        logger.info(
            f"successfully saved one on one payment history for user {user_id} refrell code is {other_user_referral_code}  subs_type {subs_type} platform {platform} amount {amount} , subscription_id {subscription_id}")

    except Exception as e:
        logger.error(f"Exception in saving payment history {traceback.format_exc()}")