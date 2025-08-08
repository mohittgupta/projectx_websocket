import traceback
import datetime

import pytz
import requests

from business_logic.mail_utils import send_email
from business_logic.object_factory import bridge_get_all_order_for_ui
from config import logger
from db.crud_utils.fx_street_news_utils.fx_street_news_read import get_all_news_current_time_based
from db.crud_utils.fx_street_news_utils.fx_street_news_write import save_news_json_data
from db.crud_utils.login_central_utils.login_central_read_queries import get_by_demo_not_expired, \
    get_by_demo_expired
from db.crud_utils.login_central_utils.login_central_write_queries import save_prev_user
from db.crud_utils.rollover_instrument_history_utils.rollover_instrument_history_read import get_all_rollover_hist
from db.crud_utils.rollover_instrument_history_utils.rollover_instrument_history_service import \
    remove_rollover_instrument_history
from db.crud_utils.trade_data_utils.trade_data_read_queries import get_by_date_alert_details, \
    count_trade_date_time, \
    trade_date_time_with_symbol
from db.models.fx_street_news import fx_street_news
import pandas as pd


def get_alerts_data(user,from_date,to_date, engine):
    try:
        data = get_by_date_alert_details(user,datetime.datetime.strptime( from_date,'%Y-%m-%d'),datetime.datetime.strptime( to_date,'%Y-%m-%d') + datetime.timedelta(days=1), engine)
        df = pd.DataFrame([vars(obj) for obj in data])
        if (len(df) > 0):
            df = df.drop(columns=['_sa_instance_state'])
            df_sorted = df.sort_values(by='row_id', ascending=False)
            df_one_column = df_sorted[['symbol','connection_name','local_symbol','inst_type','buy_sell','trade_time','tradeDate','server_date_time','user_price','order_type','alert_data','entry_id','lmt_id','stp_id','alert_status','entry_id','lmt_id','stp_id']]
            df_filled = df_one_column.fillna('')
            df_filled['tradeDate'] = df_filled['tradeDate'].astype(str)
            df_filled['server_date_time'] = df_filled['server_date_time'].astype(str)
            # df_filled['alert_data'] = df_filled['alert_data'].apply(lambda x: (x.replace("False", 'false')))
            # df_filled['alert_data'] = df_filled['alert_data'].apply(lambda x: (x.replace("'", '"')))
            return {"data": df_filled.to_dict(orient='records'), "error": False}
    except Exception as e:
        logger.error(f"error in alert data {traceback.format_exc()}")
        return {"data": [], "error": True}
    return {"data": [], "error": False}


async def start_thread_in_every_one_day(thread_run=True):
    logger.info(f"news thread is running {datetime.datetime.now()}")
    try:
        us = await get_by_demo_expired((datetime.datetime.now() - datetime.timedelta(days=5)))
        for u in us:
          logger.info(f"removing token bcz user expired {u.user_name} ")
          u.live_token = None
          u.live_token_exp = None
          u.demo_token = None
          u.demo_token_exp = None
          await save_prev_user(u)
          # break
    except Exception as e:
        logger.error(f"error in auto remove unused token {traceback.format_exc()}")
    try:
        news_data = requests.get('https://nfs.faireconomy.media/ff_calendar_thisweek.json')
        logger.info(f"news data  {news_data}")
        if(news_data.status_code == 200):
            news = news_data.json()
            for n in news:
                news_date = n['date']
                news_date = news_date.replace('T',' ')
                dt_with_offset = pd.Timestamp(news_date)
                news_date = dt_with_offset.tz_convert(pytz.UTC)

                # news_date = news_date.split('-04')[0]
                news_date = datetime.datetime.strptime(str(news_date.date()) +" "+ str(news_date.time()),'%Y-%m-%d %H:%M:%S')
                if await get_all_news_current_time_based(news_date) == None:
                    fx_news = fx_street_news()
                    fx_news.title = n['title']
                    fx_news.country = n['country']
                    fx_news.date = n['date']
                    fx_news.impact = n['impact']
                    fx_news.forecast = n['forecast']
                    fx_news.previous = n['previous']
                    fx_news.url = n['url'] if 'url' in n else ''
                    fx_news.start_date = news_date
                    await save_news_json_data(fx_news)
    except Exception as e:
        logger.error(f"error in getting news {e}")
    logger.info(f"news thread   {datetime.datetime.now()}")




async def start_open_order_thread(thread_run=True):
    logger.info(f"Open Order check Thread running {datetime.datetime.now()}")
    try:
        users = await get_by_demo_not_expired(datetime.datetime.now())
        for user in users:
            try:
                if user.demo_expiry.date() >= datetime.datetime.now().date():
                    alert_count = count_trade_date_time(datetime.datetime.now(),user.random_id)
                    logger.info(f"total count of today alert {alert_count} getting open order for client at {datetime.datetime.now().date()} {user.random_id}")
                    if alert_count > 0:
                        logger.info(f"getting open order for client at {datetime.datetime.now().date()} {user.random_id}")
                        from_date = str((datetime.datetime.now() - datetime.timedelta(days=1)).date() )
                        to_date = str((datetime.datetime.now() + datetime.timedelta(days=1)).date())
                        logger.info(f"getting open order for client at {datetime.datetime.now().date()} {user.random_id} from_date {from_date} to_date {to_date}")
                        res = await get_all_orders(user, from_date, to_date)
            except Exception as e:
                logger.error(f"error in get openorder threads user wise {traceback.format_exc()}")

            try:
                rollover_data = await get_all_rollover_hist()
                trade_data = count_trade_date_time(datetime.datetime.now(),user.random_id)
            except Exception as e:
                logger.error(f"error in sending rollover user mail {traceback.format_exc()}")

    except Exception as e:
        logger.error(f"error in open order thread {traceback.format_exc()}")
    logger.info(f"Open Order check Thread Finished {datetime.datetime.now()}")




async def rollover_mail_send(thread_run=True):
    logger.info(f"Rollover Mail Thread running {datetime.datetime.now()}")
    try:
        users = await get_by_demo_not_expired(datetime.datetime.now())
        rollover_data = await get_all_rollover_hist()
        for user in users:
            if user.user_name in ['ledmarketingcompany@gmail.com', 'alaziz@gmx.de', 'markussmart3000@gmail.com', 'stock@philosophyforsale.com']:
                continue
            try:
                data_for_user = ""
                for roll in rollover_data:
                    trade_data = trade_date_time_with_symbol(datetime.datetime.now() - datetime.timedelta(days=6),user.random_id,roll.old_contract)
                    if len(trade_data) > 0:
                        data_for_user += f"<tr> <td>{roll.old_contract}</td><td>{roll.old_contract_exp.split(' ')[0]}</td><td>{roll.new_cotract}</td>  </tr>"
                if data_for_user != "":
                    await send_email(user.user_name, subject="Contract Expiry and Rollover Notification", username="",
                               mail_type="rollover_mail",
                               user_data_dict={},
                               msg_data=data_for_user )
                    print(f'mail sent to {user.user_name} for rollover data')
            except Exception as e:
                logger.error(f"error in sending rollover user mail {traceback.format_exc()}")
    except Exception as e:
        logger.error(f"error in sending rollover user thread {traceback.format_exc()}")
    await remove_rollover_instrument_history()
    logger.info(f"Rollover Mail Thread Finished {datetime.datetime.now()}")


async def get_all_orders(user,from_date,to_date, engine='RITHMIC'):
    return await bridge_get_all_order_for_ui(user, from_date, to_date, engine=engine)


