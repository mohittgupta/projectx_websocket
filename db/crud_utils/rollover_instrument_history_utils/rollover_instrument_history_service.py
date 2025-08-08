import traceback

from config import logger
from db.crud_utils.rollover_instrument_history_utils.rollover_instrument_history_read import get_all_rollover_hist
from db.crud_utils.rollover_instrument_history_utils.rollover_instrument_history_write import save_rollover_history, \
    del_rollover_history
from db.models.rollover_instrument_history import rollover_instrument_history


async def save_rollover_instrument_history(root_symbol,old_contract,old_expiry,new_contract,new_expiry):
    try:
        logger.info(f"saving data in db root_symbol {root_symbol},old_contract {old_contract},old_expiry {old_expiry},new_contract {new_contract},new_expiry {new_expiry}")
        rih  = rollover_instrument_history()
        rih.root_symbol = root_symbol
        rih.old_contract = old_contract
        rih.new_cotract = new_contract
        rih.old_contract_exp = old_expiry
        rih.new_cotract_exp = new_expiry
        await save_rollover_history(rih)
    except Exception as e:
        logger.info(f"error in saving rollover symbol data {traceback.format_exc()}")

async def remove_rollover_instrument_history():
    try:
        rollover_hist  = await get_all_rollover_hist()
        for e in rollover_hist:
            logger.info(f"removing all rollover hist data from db {e.old_contract} {e.old_contract_exp} {e.new_cotract} {e.new_cotract_exp}  ")
            await del_rollover_history(e)
    except Exception as e:
        logger.info(f"error in removing rollover symbol data {traceback.format_exc()}")

