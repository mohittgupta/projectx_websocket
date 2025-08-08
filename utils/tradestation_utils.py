import requests

from config import logger
from db.crud_utils.multi_user_connection_utils.multi_user_read_utils import get_multi_user_engine_and_user_id


def check_instrument_exists(symbol, user):
    """Check if the instrument exists in the TradeStation database."""
    try:
        BASE_URLS = {
            "SIM": "https://sim-api.tradestation.com/v2",
            "LIVE": "https://api.tradestation.com/v2"
        }

        all_connections = get_multi_user_engine_and_user_id(engine='TRADESTATION', user_id= user.id)
        if not all_connections:
            return False , None
        for connection in all_connections:
            headers = {"Authorization": f"Bearer {connection.connection_access_token}", "Accept": "application/json"}
            base = BASE_URLS.get(connection.connection_environment, "https://sim-api.tradestation.com/v2")
            url = f"{base}/data/symbol/{symbol}"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("Name") == symbol:
                    return True , response.json()
            else:
                logger.warning(f"API failed for {symbol} on connection {connection.id}: {response.text}")
        return False , None
    except Exception as e:
        logger.error(f"Error checking instrument {symbol}: {str(e)}")
        return False , None
