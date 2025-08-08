# import traceback
#
# from config import free_multi_account, charges_per_account, logger
# from db.crud_utils.add_on_multi_accounts_utils.multi_accounts_read import get_add_on_account_by, get_add_on_by_id
# from db.crud_utils.add_on_multi_accounts_utils.multi_accounts_write import save_add_on_client
# from db.models.accounts_add_on import accounts_add_on
#
#
# def fetch_add_on_page_data(user):
#     try:
#         accounts = []
#         add_on_acc = get_add_on_account_by(user.id)
#         for acc in add_on_acc:
#             accounts.append({"id":acc.id,"client_token":acc.client_token,"client_account_id":acc.client_account_id,"active":acc.active,"updatable":acc.updatable,
#                              "payment_in":acc.payment_in,"payment_expiry":acc.payment_expiry,"subscription_id":acc.subscription_id })
#         res = {"free_account":free_multi_account,"activated_account":user.max_multi_account,"charges_per_account":charges_per_account,"accounts":accounts,"current_limit":user.max_multi_account}
#         return res, False
#     except Exception as e:
#         logger.error(f"error in fetching add on {traceback.format_exc()}")
#         return "Invalid code", True
#
# def save_add_on_page_data(user,client_id,client_token,client_account_id):
#     try:
#         add_on_acc = get_add_on_account_by(user.id)
#         if client_id == 0 and user.max_multi_account <= len(add_on_acc):
#             return "Max Account Add Done. If you want to add more account please pay first",True
#         else:
#             if client_id != 0:
#                 add_on = get_add_on_by_id(client_id)
#                 if add_on == None:
#                     return "Not Edit-able", True
#                 elif not add_on.updatable:
#                     return "Not Edit-able", True
#             else:
#                 add_on = accounts_add_on()
#             add_on.user = user.id
#             add_on.client_token = client_token
#             add_on.client_account_id = client_account_id
#             add_on.active = True
#             add_on.updatable = True
#             save_add_on_client(add_on)
#         return "Successfully Saved", False
#     except Exception as e:
#         logger.error(f"error in adding adds on {traceback.format_exc()}")
#         return "Invalid code", True