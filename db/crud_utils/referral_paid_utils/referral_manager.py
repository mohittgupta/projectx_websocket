import traceback

from config import logger
from db.crud_utils.referral_paid_utils.referred_user_info import ReferredUsersInfo

from db.models.login_central import login_central


class ReferralManager:
    async def get_referred_users_info(self, user: login_central):
        try:
            referred_users_info = ReferredUsersInfo(
                user=user
            )
            await referred_users_info.execute()
            referred_users_info_response = await referred_users_info.get_info()
            referred_users_json_response = referred_users_info_response.to_dict()
            logger.debug(f"Referred User Info Response : {referred_users_info_response}")
            return referred_users_json_response
        except Exception as e:
            logger.error(f"Exception while fetching referred-user-info : {traceback.format_exc()}")
            raise e