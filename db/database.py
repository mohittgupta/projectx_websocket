from config import logger,db_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import database_exists, create_database




def database_create(engine):
    if not database_exists(engine.url):
        create_database(engine.url)

engine = create_engine(db_url)
database_create(engine)
db_session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
def init_db():
    from db.models import rollover_data, referral_paid,manual_trade_pause_accounts,subscription_refund,permission,sub_accounts,payment_history,user_proxy,trade_max_retry_check,manual_trade_pause,watch_client_order_id_map,rollover_instrument_history,fx_street_news,news_trade_pause,news_symbol_mapping,multi_accounts,robinhood_orders,robinhood_access_token,mail_trigger,tradovate_accounts,discount,login_central,server_start_time,trade_setting,trade_data,order_data,contract_info,payment_init,payment_event,subscription_init
    from db.models.projectx_data import Projectx_Orders, Projectx_Trades, Projectx_Positions
    Base.metadata.create_all(bind=engine)
init_db()
logger.info("************************************************************************")




# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
#
# from config import logger, db_url, on_off_async_db
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy_utils import database_exists, create_database
#
# def database_create(database_url):
#     if not database_exists(database_url):
#         create_database(database_url)
#
# db_session = None
# if on_off_async_db:
#     sync_database_url = db_url.replace("postgresql+asyncpg", "postgresql")
#     database_create(sync_database_url)
#     engine = create_async_engine(db_url, echo=True)
#     db_session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine, expire_on_commit=False, class_=AsyncSession))
# else:
#     database_create(db_url)
#     engine = create_engine(db_url)
#     db_session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
# Base = declarative_base()
# Base.query = db_session.query_property()
# def init_db():
#     from db.models import trade_max_retry_check,manual_trade_pause,watch_client_order_id_map,rollover_instrument_history,fx_street_news,news_trade_pause,news_symbol_mapping,multi_accounts,robinhood_orders,robinhood_access_token,mail_trigger,tradovate_accounts,discount,login_central,server_start_time,trade_setting,trade_data,order_data,contract_info,payment_init,payment_event,subscription_init
#     Base.metadata.create_all(bind=engine)
# init_db()
# logger.info("************************************************************************")
#
