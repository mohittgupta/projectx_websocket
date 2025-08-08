import datetime
import json
import traceback

from config import logger, monthly_product_id, yearly_product_id, subscriptions, quarter_product_id, free_multi_account, \
    charges_per_account, paddel_token
from db.crud_utils.discount_utils.discount_read_queries import get_all_discount_order, get_by_code_discount_order, \
    get_by_code_discount_order_active
from db.crud_utils.discount_utils.discount_write_queries import save_discount_details
from db.crud_utils.login_central_utils.login_central_write_queries import save_prev_user
from db.crud_utils.subscription_utils.subscription_read import get_last_active_subscription
from db.models.discount import discount
from gateway.paddle_api import create_paddel_plan
from gateway.paypal_payment_api import get_auth_token, create_plan


async def save_discount_code(code,disc,status,expiry):
    try:
        token = await get_auth_token()
        if token == None:
            return "Auth token not found, cannot save discount code"
        msg = "Successfully updated"
        data = await get_by_code_discount_order(code)
        if data == None:
            data = discount()
            msg = "Successfully created"

        monthly_amount,yearly_amount,quarterly_amount=0,0,0
        paddel_monthly_product_id, paddel_yearly_product_id, paddel_quarterly_product_id = "","",""
        for key,value in list(subscriptions.items()):
            if value['expiry_day'] == 30:
                monthly_amount = value['real_amount']
                paddel_monthly_product_id = value['paddel_product_id']
            elif value['expiry_day'] == 365:
                yearly_amount = value['real_amount']
                paddel_yearly_product_id = value['paddel_product_id']
            elif value['expiry_day'] == 91:
                quarterly_amount = value['real_amount']
                paddel_quarterly_product_id = value['paddel_product_id']



        data.code = code
        data.discount = disc
        data.monthly_product_id = monthly_product_id
        data.yearly_product_id = yearly_product_id
        data.quarterly_product_id = quarter_product_id

        data.monthly_amount = round(monthly_amount - ((monthly_amount / 100) * disc),2)
        data.yearly_amount = round(yearly_amount - ((yearly_amount/ 100) * disc),2)
        data.quarterly_amount = round(quarterly_amount - ((quarterly_amount / 100) * disc), 2)

        month_id = await create_plan(monthly_product_id, data.monthly_amount, recurring_day='MONTH', token=token)
        data.monthly_plan_id = month_id
        year_id = await create_plan(yearly_product_id, data.yearly_amount, recurring_day='YEAR', token=token)
        data.yearly_plan_id = year_id
        quater_id = await create_plan(quarter_product_id, data.quarterly_amount, recurring_day='QUARTER', token=token)
        data.quarterly_plan_id = quater_id

        # paddel_month_id = create_paddel_plan(paddel_monthly_product_id, data.monthly_amount, recurring_day='MONTH', token=paddel_token)
        # logger.info(f"set discount code paddel price id {paddel_month_id}  monthly_amount {data.monthly_amount}")
        # data.paddel_monthly_plan_id = paddel_month_id
        # paddel_year_id = create_paddel_plan(paddel_yearly_product_id, data.yearly_amount, recurring_day='YEAR', token=paddel_token)
        # logger.info(f"set discount code paddel price id {paddel_year_id}  yearly_amount {data.yearly_amount}")
        # data.paddel_yearly_plan_id = paddel_year_id
        # paddel_quater_id = create_paddel_plan(paddel_quarterly_product_id, data.quarterly_amount, recurring_day='QUARTER', token=paddel_token)
        # data.paddel_quarterly_plan_id = paddel_quater_id
        # logger.info(f"set discount code paddel price id {paddel_quater_id}  quarterly_amount {data.quarterly_amount}")

        paddel_month_id = ''
        paddel_year_id = ''
        paddel_quater_id = ''
        data.paddel_monthly_plan_id = paddel_month_id
        data.paddel_yearly_plan_id = paddel_year_id
        data.paddel_quarterly_plan_id = paddel_quater_id


        data.expired = datetime.datetime.strptime(expiry, '%Y-%m-%d')
        data.active = status
        await save_discount_details(data)
        return msg
    except Exception as e:
        logger.error(f"error in adding discountcode {traceback.format_exc()}")
        return f"{e}"



def fetch_discount_code():
    try:
        res =[]
        data = get_all_discount_order()
        for d in data:
            res.append({
                "id": d.id,
                "code": d.code,
                "discount": d.discount,
                "monthly_product_id": d.monthly_product_id,
                "yearly_product_id": d.yearly_product_id,
                "quarterly_product_id": d.quarterly_product_id,
                "monthly_plan_id": d.monthly_plan_id,
                "yearly_plan_id": d.yearly_plan_id,
                "quarterly_plan_id": d.quarterly_plan_id,
                "expired": d.expired.isoformat() if d.expired else None,
                "status": d.active,
                "monthly_amount": d.monthly_amount,
                "quarterly_amount": d.quarterly_amount,
                "yearly_amount": d.yearly_amount
            })

        return res
    except Exception as e:
        logger.error(f"error in adding discountcode {traceback.format_exc()}")
        return []

async def add_discount_coupon_code(user,code):
    try:
        if code == "":
            logger.info(f"{user.user_name}  adding code {code}")
            user.other_referral_code = code
            await save_prev_user(user)
        else:
            logger.info(f"{user.user_name}  adding code {code}")
            discount = get_by_code_discount_order_active(code)
            if discount == None:
                logger.info(f"{user.user_name}  invalid code {code} ")
                return "Invalid code", True
            else:
                if(datetime.datetime.now().date() > discount.expired.date()):
                    logger.info(f"{user.user_name}  code expired {code} ")
                    return "Code Expired", True
                else:
                    logger.info(f"{user.user_name}  code all done {code} ")
                    user.other_referral_code = code
                    await save_prev_user(user)
        return "Discount Attached", False
    except Exception as e:
        logger.error(f"error in adding discountcode {traceback.format_exc()}")
        return "Invalid code", True


def fetch_subscription_page_data(user):
    try:
        code = user.other_referral_code if user != None and user.other_referral_code != None and user.other_referral_code != "" else None
        discount_percentage = None
        if code != None:
            discount = get_by_code_discount_order_active(code)
            if discount != None and (datetime.datetime.now().date() < discount.expired.date()):
                discount_percentage = discount.discount

        f = open("subscription.json", )
        subs = json.load(f)
        subscription = subs
        f.close()
        monthly_amount,yearly_amount=0,0
        for key,value in list(subscription.items()):
            if value['expiry_day'] == 30:
                monthly_amount = value['real_amount']
                if discount_percentage !=None:
                    value['real_amount'] = round(value['real_amount'] - ((monthly_amount / 100) * discount_percentage),2)
            elif value['expiry_day'] == 91:
                quart_amount = value['real_amount']
                if discount_percentage !=None:
                    value['real_amount'] = round(value['real_amount'] - ((quart_amount/ 100) * discount_percentage),2)
            elif value['expiry_day'] == 365:
                yearly_amount = value['real_amount']
                if discount_percentage !=None:
                    value['real_amount'] = round(value['real_amount'] - ((yearly_amount/ 100) * discount_percentage),2)

        return subscription, False
    except Exception as e:
        logger.error(f"error in adding discountcode {traceback.format_exc()}")
        return "Invalid code", True



def fetch_add_on_page_data(user):
    try:
        res = {"free_account":free_multi_account,"activated_account":user.max_multi_account,"charges_per_account":charges_per_account}
        return res, False
    except Exception as e:
        logger.error(f"error in adding discountcode {traceback.format_exc()}")
        return "Invalid code", True