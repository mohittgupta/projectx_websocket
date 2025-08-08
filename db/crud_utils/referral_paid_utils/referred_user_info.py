from typing import Optional



from db.crud_utils.login_central_utils.login_central_read_queries import user_connected_users
from db.crud_utils.payment_history_utils.payment_history_read import (
    get_current_payment_history, get_all_payment_history
)
from db.crud_utils.referral_paid_utils.referral_paid_read import get_all_paid_referral_by_user_id
from db.crud_utils.subscription_refund_utils.subscription_refund_read import get_refunds_of_user
from db.crud_utils.trade_data_utils.trade_data_read_queries import is_trade_exists_by_random_id
from db.crud_utils.tradovate_accounts_utils.tradovate_accounts_read import get_tradovate_accounts_by_user_id, \
    get_tradovate_accounts_by_userid
from db.dtos.referral_dtos import ReferredUsersResponseDTO, ReferredSummaryDTO, UserInfoDTO, ReferredUserInfoDTO, \
    PMTReferredInfoDTO
from db.models.login_central import login_central


class ReferredUsersInfo:
    def __init__(self, user: login_central) -> None:
        self.user = user

        self.user_info_dto: Optional[UserInfoDTO] = None
        self.referred_user_info_dtos = []
        self.referred_users_response_dto: Optional[ReferredUsersResponseDTO] = None
        self.referred_summary_dto: Optional[ReferredSummaryDTO] = None
        self.pmt_referred_info_dtos = []
        self.total_amount_by_pmt = 0

        self.subscription_to_months = {
            "30 days": 1,
            "91 days": 3,
            "365 days": 12
        }

    async def execute(self):
        await self._fetch_user_info()
        await self._fetch_referred_users()
        await self._prepare_referral_summary()
        await self._fetch_payment_by_pmt_to_referrals()

    async def get_info(self):
        self.referred_users_response_dto = ReferredUsersResponseDTO(
            user_info_dto=self.user_info_dto,
            referred_user_info_dtos=self.referred_user_info_dtos,
            referred_summary_dto=self.referred_summary_dto,
            pmt_referred_info_dtos=self.pmt_referred_info_dtos,
            total_payment_by_pmt=self.total_amount_by_pmt
        )
        return self.referred_users_response_dto

    async def _fetch_user_info(self):
        payment_refunds = await get_refunds_of_user(self.user.id)
        total_amount_refund = sum(payment_rf.amount for payment_rf in payment_refunds)
        self.user_info_dto = UserInfoDTO(
            user_id=self.user.id,
            user_random_id=self.user.random_id,
            user_email=self.user.user_name,
            total_amount_refund =total_amount_refund
        )

    async def _fetch_referred_users(self):
        referred_users = await user_connected_users(self.user.my_referral_code)

        for referred_user in referred_users:
            first_alert_sent = await is_trade_exists_by_random_id(referred_user.random_id)
            tradovate_account = bool(get_tradovate_accounts_by_userid(referred_user.random_id))
            current_payment_history = await get_current_payment_history(referred_user.id)
            payment_histories = await get_all_payment_history(referred_user.id)
            payment_refunds = await get_refunds_of_user(referred_user.id)

            total_month_paid = sum(
                self.subscription_to_months.get(payment.subscription_type, 0) for payment in payment_histories
            )
            total_amount_paid = sum(payment.amount for payment in payment_histories)
            total_amount_refund = sum(payment_rf.amount for payment_rf in payment_refunds)

            self.referred_user_info_dtos.append(ReferredUserInfoDTO(
                referral_email=referred_user.user_name,
                first_alert_sent=first_alert_sent,
                tradovate_connected=tradovate_account,
                current_plan=current_payment_history.subscription_type if current_payment_history else None,
                current_plan_start_date=current_payment_history.created if current_payment_history else None,
                current_plan_payment_amount=current_payment_history.amount if current_payment_history else 0,
                total_month_paid=total_month_paid,
                total_amount_paid=total_amount_paid,
                total_amount_refund = total_amount_refund
            ))

    async def _prepare_referral_summary(self):
        self.referred_summary_dto = ReferredSummaryDTO(
            total_referred_users=len(self.referred_user_info_dtos),
            total_paid_referred_users=sum(1 for user in self.referred_user_info_dtos if user.total_amount_paid > 0),
            total_referred_users_amount=sum(user.total_amount_paid for user in self.referred_user_info_dtos),
            total_referred_months=sum(user.total_month_paid for user in self.referred_user_info_dtos),
            total_amount_refund = sum(user.total_amount_refund for user in self.referred_user_info_dtos)

        )

    async def _fetch_payment_by_pmt_to_referrals(self):
        paid_referrals = await get_all_paid_referral_by_user_id(self.user.id)

        self.pmt_referred_info_dtos = [
            PMTReferredInfoDTO(
                payment_date=paid_referral.paid_date,
                payment_amount=paid_referral.amount,
                payment_mode=paid_referral.payment_mode
            )
            for paid_referral in paid_referrals
        ]

        self.total_amount_by_pmt = sum(paid_referral.amount or 0.0 for paid_referral in paid_referrals)
