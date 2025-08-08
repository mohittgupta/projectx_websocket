import datetime
import json
from dataclasses import dataclass, asdict

from config import logger


@dataclass
class UserDto:
    id : int =0
    user_name : str = ""
    parent_mail : str = ""
    password : str = ""
    random_id : str = ""
    live_account_id : int = 0
    demo_account_id : int = 0
    paid : bool = False
    payment_in : datetime = None
    payment_exp : datetime = None
    live_token : str = ""
    live_token_exp : datetime = None
    demo_token : str = ""
    demo_token_exp : datetime = None
    demo : bool = False
    demo_expiry : datetime = None
    reset_link : str = ""
    reset_link_exp : datetime = None
    demo_account_name : str = ""
    live_account_name : str = ""
    pause : bool = False
    profit_goal : float = 0
    loss_goal : float = 0
    max_loss_created : bool = False
    my_referral_code : str = ""
    other_referral_code : str = ""
    other_user_referral_code : str = ""
    mail_verified : bool = False
    mail_verification_token : str = ""
    demo_mail_send : datetime = None
    authtoken : str = ""
    exetoken : str = ""
    error_instruction_mail_flag : datetime = None
    discount_promotional_flag : datetime = None
    created : datetime = None
    demo_disconnect_flag : datetime = None
    no_right_trade_flag : datetime = None
    no_trade_flag : datetime = None
    unsubscribe : bool = False
    phone_no : str = ""
    source : str = ""
    payment_mail : datetime = None
    max_multi_account : int = 0
    rollover_mail_send : datetime = None


    def __str__(self):
            return json.dumps(asdict(self))

