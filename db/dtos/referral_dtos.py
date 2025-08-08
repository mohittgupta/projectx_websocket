from dataclasses import dataclass, asdict

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


@dataclass
class UserInfoDTO:
    user_id: int
    user_random_id: str
    user_email: str
    total_amount_refund: Optional[str] = 0

@dataclass
class ReferredUserInfoDTO:
    referral_email: Optional[str] = None
    first_alert_sent: Optional[bool] = None
    tradovate_connected: Optional[bool] = None
    current_plan: Optional[str] = None
    current_plan_start_date: Optional[datetime] = None
    current_plan_payment_amount: Optional[float] = None
    total_month_paid: Optional[int] = None
    total_amount_paid: Optional[float] = None
    total_amount_refund : Optional[float] = None

@dataclass
class ReferredSummaryDTO:
    total_referred_users: Optional[int] = None
    total_paid_referred_users: Optional[int] = None
    total_referred_users_amount: Optional[float] = None
    total_referred_months: Optional[int] = None
    total_amount_refund: Optional[float] = None

@dataclass
class PMTReferredInfoDTO:
    payment_date: Optional[datetime] = None
    payment_amount: Optional[float] = None
    payment_mode: Optional[str] = None

@dataclass
class ReferredUsersResponseDTO:
    user_info_dto: Optional[UserInfoDTO] = None
    referred_user_info_dtos: Optional[List[ReferredUserInfoDTO]] = None
    referred_summary_dto: Optional[ReferredSummaryDTO] = None
    pmt_referred_info_dtos: Optional[List[PMTReferredInfoDTO]] = None
    total_payment_by_pmt: Optional[float] = 0.0

    def to_dict(self) -> dict:
        def convert(value: Any) -> Any:
            if isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, list):
                return [convert(item) for item in value]
            elif isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            else:
                return value

        raw_dict = asdict(self)
        return convert(raw_dict)
