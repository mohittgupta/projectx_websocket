

from db.database import Base
from sqlalchemy import Column, Integer, String,Boolean,DateTime,Float

class login_central(Base):
    __tablename__ = 'login_central'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_name = Column(String())
    password = Column(String())
    password_hash = Column(String())
    random_id = Column(String())
    live_account_id = Column(Integer())
    demo_account_id = Column(Integer())
    paid = Column(Boolean())
    payment_in = Column(DateTime())
    payment_exp = Column(DateTime())
    live_token = Column(String())
    live_token_exp = Column(DateTime())
    demo_token = Column(String())
    demo_token_exp = Column(DateTime())
    demo = Column(Boolean())
    demo_expiry = Column(DateTime())
    reset_link = Column(String())
    reset_link_exp = Column(DateTime())
    demo_account_name = Column(String())
    live_account_name = Column(String())
    pause = Column(Boolean())
    profit_goal = Column(Float())
    loss_goal = Column(Float())
    max_loss_created = Column(Boolean())
    my_referral_code = Column(String())
    other_referral_code = Column(String())

    other_user_referral_code = Column(String())
    mail_verified = Column(Boolean())
    mail_verification_token = Column(String())
    demo_mail_send = Column(DateTime())
    authtoken = Column(String())
    exetoken = Column(String())
    admin_token = Column(String())
    error_instruction_mail_flag = Column(DateTime())
    discount_promotional_flag = Column(DateTime())

    created = Column(DateTime())
    demo_disconnect_flag = Column(DateTime())
    no_right_trade_flag = Column(DateTime())
    no_trade_flag = Column(DateTime())
    unsubscribe = Column(Boolean())
    phone_no = Column(String())
    source = Column(String())
    payment_mail = Column(DateTime())
    max_multi_account = Column(Integer())
    ib_app_download = Column(Boolean(), default=False)
    rollover_mail_send = Column(DateTime())
    ib_app_download_source = Column(String())

