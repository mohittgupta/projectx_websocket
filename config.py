import datetime
import json
import logging
from logging.config import dictConfig
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
import uuid

import redis
from starlette.middleware.base import BaseHTTPMiddleware


executor = ThreadPoolExecutor(100)


#  for default login
default_user = 'admin'
default_password = 'admin'
#  flask details
flask_host = "0.0.0.0"
flask_port = 5000
redis_contract_info = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True,db=0)
redis_proxy = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True,db=1)
login_central_redis = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True,db=2)

#  empty otherwise UTC
default_setting = {"timezone":""}

token_expiry_time_zone = {"timezone":""}
#******************************

#  Database ---------------
# db_url = 'sqlite:///tradovate.db'
db_url = "postgresql://postgres:postgres@localhost:5432/rithmic_new"

from contextvars import ContextVar
request_id_var = ContextVar("request_id", default="N/A")

# Middleware for generating and storing the request ID
class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
    async def dispatch(self, request, call_next):
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)

        try:
            js_check = await request.json()  # Parse JSON body
            token = js_check.get('token', None)
            symbol = js_check.get('symbol', None)
        except Exception as e:
            print(f"Error extracting token: {e}")  # Handle cases where JSON parsing fails
            token = ''
            symbol = ''

        request.state.token = token
        request.state.token_symbol = f"{symbol}_{token}"
        # Store the request ID in the context variable
        print(f"Generated Request ID: {request_id}")  # Debug statement
        response = await call_next(request)
        return response


# Logging filter to include request ID in logs
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get("N/A")
        return True
#  Flask secret key
secret_key="tradovate12022021"
#  logging
log_Date = 'app'
logging_type = "DEBUG"
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,



    'formatters': {
        'default': {
            'format': '%(threadName)s - %(thread)d - %(asctime)s  - %(name)s - %(funcName)s - %(lineno)d - %(levelname)s - [%(request_id)s] - %(message)s'
        }
    },
'filters': {
        'request_id_filter': {  # Define the filter
            '()': RequestIDFilter  # Instantiate the custom filter
        }
    },
    'handlers': {
        'debugfilehandler': {
            'level': logging_type,
            'class': 'logging.FileHandler',
            'filename': log_Date+'.log',
            'formatter': 'default',
            'filters': ['request_id_filter']
        },
        'rotatingfile': {
            'maxBytes': 2 * 1024 * 1024 * 40,
            'backupCount': 10,
            'level': logging_type,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_Date+'.log',
            'formatter': 'default',
            'filters': ['request_id_filter']
        },
        'consolehandler': {
            'level': logging_type,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'filters': ['request_id_filter']
        }
    },
    'loggers': {
        'app': {
            'handlers': [ 'consolehandler','rotatingfile'],
            'level': logging_type,
            'propogate': True,
        },
        'console': {
            'handlers': ['consolehandler'],
            'level': logging_type,
            'propogate': True
        }
    }
}

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('app')

default_min_tick = 0.25
default_symbol_with_ticks ={"Symbol":"RTYM2024","LocalSymbol":"RTYM4","LotSize":50.0,"MinTick":0.1 },            {"Symbol":"NQM2024","LocalSymbol":"NQM4","LotSize":20.0,"MinTick":0.25 },    {"Symbol":"GCM2024","LocalSymbol":"GCM4","LotSize":100.0,"MinTick":0.1 },    {"Symbol":"6BM2024","LocalSymbol":"6BM4","LotSize":62500.0,"MinTick":0.0001 },    {"Symbol":"6EM2024","LocalSymbol":"6EM4","LotSize":125000.0,"MinTick":0.00005 },    {"Symbol":"6CM2024","LocalSymbol":"6CM4","LotSize":100000.0,"MinTick":0.00005 },    {"Symbol":"6AM2024","LocalSymbol":"6AM4","LotSize":100000.0,"MinTick":0.0001 },    {"Symbol":"CLM2024","LocalSymbol":"CLM4","LotSize":1000.0,"MinTick": 0.01},    {"Symbol":"6SM2024","LocalSymbol":"6SM4","LotSize":125000.0,"MinTick":0.0001 },    {"Symbol":"6NM2024","LocalSymbol":"6NM4","LotSize":100000.0,"MinTick":0.00005 },    {"Symbol":"YMM2024","LocalSymbol":"YMM4","LotSize":5.0,"MinTick":1.0 },    {"Symbol":"MYMM2024","LocalSymbol":"MYMM4","LotSize":0.5,"MinTick":1.0 },    {"Symbol":"MESM2024","LocalSymbol":"MESM4","LotSize":5.0,"MinTick":0.25 },    {"Symbol":"MNQM2024","LocalSymbol":"MNQM4","LotSize":2.0,"MinTick":0.25 },     {"Symbol":"MGCM2024","LocalSymbol":"MGCM4","LotSize":10.0,"MinTick": 0.1},{"Symbol":"MCLM2024","LocalSymbol":"MCLM4","LotSize":100.0,"MinTick": 0.01},     {"Symbol":"M2K2024","LocalSymbol":"M2K4","LotSize":5.0,"MinTick": 0.1},{"Symbol":"ESM2024","LocalSymbol":"ESM4","LotSize":50.0,"MinTick": 0.25},     {"Symbol":"6JM2024","LocalSymbol":"6JM4","LotSize":12500000.0,"MinTick": 0.0000005}
# root_symbol=['RTY','NQ','GC','6B','6E','6C','6A','CL','6S','6N','YM','MYM','MES','MNQ','MGC','MCL','M2','ES','6J' ,'ZF','ZN','TN','ZB','UB' ]
root_symbol_exchange=[{'RTY':'CME'}, {'NQ':'CME'}, {'GC':'COMEX'}, {'6B':'CME'}, {'6E':'CME'}, {'6C':'CME'}, {'6A':'CME'}, {'CL':'NYMEX'}, {'6S':'CME'},
                      {'6N':'CME'}, {'YM':'CBOT'}, {'MYM':'CBOT'}, {'MES':'CME'}, {'MNQ':'CME'}, {'MGC':'COMEX'}, {'MCL':'NYMEX'}, {'M2':'CME'},
                      {'ES':'CME'}, {'6J':'CME'} , {'ZF':'CBOT'}, {'ZN':'CBOT'}, {'TN':'CBOT'}, {'ZB':'CBOT'}, {'UB':'CBOT'},{'ZL':'CBOT'} ,{'M6E':'CME'}, {'SI': 'COMEX'},{'PL':'NYMEX'} ]

f = open("tradovate_config.json", )
data = json.load(f)
paypal_secret_key = data['paypal_secret_key']
paypal_client_id = data['paypal_client_id']
paddel_frontend_callback = data['paddel_frontend_callback']
proxy_user_name = data['proxy_user_name']
proxy_password = data['proxy_password']
paypal_url = data['paypal_url']
monthly_product_id = data['monthly_product_id']
yearly_product_id = data['yearly_product_id']
quarter_product_id = data['quarter_product_id']
paddel_client_token = data['paddel_client_token']
paddel_token = data['paddel_token']
paddel_url = data['paddel_url']

frontend_url = data['frontend_url']
page_url = data['page_url']
redirect_url = data['redirect_url']
cid = data['cid']
sec = data['sec']
tradovate_oauth_url=data['tradovate_oauth_url']+'?response_type=code&client_id='+str(data['cid'])+'&redirect_uri='
demo_access_token_url = data['demo_access_token_url']
live_access_token_url = data['live_access_token_url']
tradovate_live_url=data['tradovate_live_url']
tradovate_demo_url= data['tradovate_demo_url']
razorpay_key= data['razorpay_key']
razorpay_secret = data['razorpay_secret']
reset_link = data['reset_link']
f.close()

smtp_server = data['smtp_server']
smtp_port=data['smtp_port']
sender_mail =data['smtp_email']
sender_password = data['smtp_password']
sender_username = data['smtp_username']


app_obj= {"app":None}



admin_url= ['bhavishyagoyal@gmail.com' , 'ermohitgupta.16@gmail.com']

rithmic_url = "http://127.0.0.1:5001"
rithmic_app_version='0.0.0.1'
rithmic_app_name={'Rithmic Test':'hftsolution','Rithmic Paper Trading':'hftsolution',
              'TopstepTrader':'hftsolution','SpeedUp':'hftsolution','TradeFundrr':'hftsolution',
              'UProfitTrader':'hftsolution','Apex':'hftsolution','MES Capital':'hftsolution',
            'Rithmic 01':'hftsolution',
              'TheTradingPit':'hftsolution','FundedFuturesNetwork':'hftsolution','Bulenox':'hftsolution'
              ,'PropShopTrader':'hftsolution','4PropTrader':'hftsolution','FastTrackTrading':'hftsolution', 'ThriveTrading':'hftsolution'}

rithmic_uri= {'Rithmic Test':'wss://rituz00100.rithmic.com:443',
              'Rithmic Paper Trading':'wss://rprotocol.rithmic.com:443',
                'Rithmic 01':'wss://rprotocol.rithmic.com:443',
              'TopstepTrader':'wss://rprotocol.rithmic.com:443',
              'SpeedUp':'wss://rprotocol.rithmic.com:443',
              'TradeFundrr':'wss://rprotocol.rithmic.com:443',
              'UProfitTrader':'wss://rprotocol.rithmic.com:443',
              'Apex':'wss://rprotocol.rithmic.com:443',
              'MES Capital':'wss://rprotocol.rithmic.com:443',
              'TheTradingPit':'wss://rprotocol.rithmic.com:443',
              'FundedFuturesNetwork':'wss://rprotocol.rithmic.com:443',
              'Bulenox':'wss://rprotocol.rithmic.com:443'
              ,'PropShopTrader':'wss://rprotocol.rithmic.com:443',
              '4PropTrader':'wss://rprotocol.rithmic.com:443',
              'FastTrackTrading':'wss://rprotocol.rithmic.com:443',
              'ThriveTrading':'wss://rprotocol.rithmic.com:443'}

default_engine = 'TRADOVATE'
supported_broker  = {'TRADOVATE':'Tradovate','RITHMIC':'Rithmic' , 'IB' :'IB', 'TRADELOCKER': 'TRADELOCKER', 'TRADESTATION':'TRADESTATION', 'PROJECTX':'PROJECTX'}

unique_request_code = 'vbdhkeshu124dfjk7fjk3'
tradovate_sock_unique_code = 'sddgd32423&*(bgdEVsddgT'
salt= b'Goyal@vndujf17385jdfifgmfv^&*$vfdfFGHdfraja57DJLO89Ggdfgfdyg!!vbnjDFYyfhfggu486t547h5yh4nt65g7;;6][dfBCVgf54gfgg'

tradovate_sock_url = 'http://34.47.29.80/socket'
config_contract_details = {}
config_contract_details_by_name = {}
first_product_id = 0
free_multi_account = 2
charges_per_account = 3


ib_url = "https://api.pickmytrade.io/wbsk"
ib_rollover_user = 'bhavishyagoyal@gmail.com'

max_check_per_minute_config = 50


on_off_async_db = False


async_sleep_for_tradovate_request = 2


user_proxy_obj={}

SQLALCHEMY_SECRET = 'PickMyTrade'


# ------------------------------- TRADE STATION --------------------------
trade_station_key = '80vRDp0zdmw0z2icMTa2FGzP1ryx5NrM'
trade_station_secret = 'OohEaSGXoyvdYUS1QmJjREIGwjfvCDvAJJf5-Rgu0Q07FdJK8xMdqmIhyxBcA4tf'
trade_station_port = 3000
trade_station_redirect_uri = "https://app.pickmytrade.io/tradestation/callback"
AUTH_URL = "https://signin.tradestation.com/authorize"
tradestation_admin_email = 'ermohitgupta.16@gmail.com'
payment_exp_admin = ['bhavishyagoyal@gmail.com','johannbirletrade@gmail.com','rajayadav1997@yahoo.com']

#-------------------------------------- Project X configs --------------------------------------------------------------
projectx_user_hubs = {
    "demo": "https://gateway-rtc-demo.s2f.projectx.com/hubs/user",
    "alphaticks": "https://rtc.alphaticks.projectx.com/hubs/user",
    "blueguardianfutures": "https://rtc.blueguardianfutures.projectx.com/hubs/user",
    "blusky": "https://rtc.blusky.projectx.com/hubs/user",
    "e8": "https://rtc.e8.projectx.com/hubs/user",
    "fundingfutures": "https://rtc.fundingfutures.projectx.com/hubs/user",
    "thefuturesdesk": "https://rtc.thefuturesdesk.projectx.com/hubs/user",
    "futureselite": "https://rtc.futureselite.projectx.com/hubs/user",
    "fxifyfutures": "https://rtc.fxifyfutures.projectx.com/hubs/user",
    "goatfundedfutures": "https://rtc.goatfundedfutures.projectx.com/hubs/user",
    "tickticktrader": "https://rtc.tickticktrader.projectx.com/hubs/user",
    "toponefutures": "https://rtc.toponefutures.projectx.com/hubs/user",
    "topstepx": "https://rtc.topstepx.com/hubs/user",
    "tx3funding": "https://rtc.tx3funding.projectx.com/hubs/user"
}

projectx_api_endpoints = {
    "demo": "https://gateway-api-demo.s2f.projectx.com/api",
    "alphaticks": "https://api.alphaticks.projectx.com/api",
    "blueguardianfutures": "https://api.blueguardianfutures.projectx.com/api",
    "blusky": "https://api.blusky.projectx.com/api",
    "e8": "https://api.e8.projectx.com/api",
    "fundingfutures": "https://api.fundingfutures.projectx.com/api",
    "thefuturesdesk": "https://api.thefuturesdesk.projectx.com/api",
    "futureselite": "https://api.futureselite.projectx.com/api",
    "fxifyfutures": "https://api.fxifyfutures.projectx.com/api",
    "goatfundedfutures": "https://api.goatfundedfutures.projectx.com/api",
    "tickticktrader": "https://api.tickticktrader.projectx.com/api",
    "toponefutures": "https://api.toponefutures.projectx.com/api",
    "topstepx": "https://api.topstepx.com/api",
    "tx3funding": "https://api.tx3funding.projectx.com/api"
}

oco_api_endpoints = {"topstepx": 'https://userapi.topstepx.com/Order/editStopLoss',
                    "alphaticks": 'https://userapi.alphaticks.projectx.com/api/Order/editStopLoss',
                    "blueguardianfutures": 'https://userapi.blueguardianfutures.projectx.com/api/Order/editStopLoss',
                    "blusky": 'https://userapi.blusky.projectx.com/api/Order/editStopLoss',
                    "e8": 'https://userapi.e8.projectx.com/api/Order/editStopLoss',
                    "fundingfutures": 'https://userapi.fundingfutures.projectx.com/api/Order/editStopLoss',
                    "thefuturesdesk": 'https://userapi.thefuturesdesk.projectx.com/api/Order/editStopLoss',
                    "futureselite": 'https://userapi.futureselite.projectx.com/api/Order/editStopLoss',
                    "fxifyfutures": 'https://userapi.fxifyfutures.projectx.com/api/Order/editStopLoss',
                    "goatfundedfutures": 'https://userapi.goatfundedfutures.projectx.com/api/Order/editStopLoss',
                    "tickticktrader": 'https://userapi.tickticktrader.projectx.com/api/Order/editStopLoss',
                    "toponefutures": 'https://userapi.toponefutures.projectx.com/api/Order/editStopLoss',
                    "tx3funding": 'https://userapi.tx3funding.projectx.com/api/Order/editStopLoss'
                    }


PROJECTX_ORDER_STATUS = {
    0: "None",
    1: "Open",
    2: "Filled",
    3: "Cancelled",
    4: "Expired",
    5: "Rejected",
    6: "Pending"
}

PROJECTX_ORDER_TYPE = {
    0: "Unknown",
    1: "Limit",
    2: "Market",
    3: "StopLimit",
    4: "Stop",
    5: "TrailingStop",
    6: "JoinBid",
    7: "JoinAsk"
}


PROJECTX_Sending_ORDER_TYPE = {
    0: "Unknown",
    1: "LMT",
    2: "MKT",
    3: "STPLMT",
    4: "STP",
    5:"STPTRAIL"
}


front_backet_url = ''
code_frontend = ''