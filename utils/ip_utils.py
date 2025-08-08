from datetime import datetime
from ipaddress import ip_address

from fastapi import Request as request

from config import logger as log

from datetime import datetime
from ipaddress import ip_address
from fastapi import Request
from config import logger as log


def get_valid_ip(request: Request, do_logging: bool = True):
    '''
    Get valid client IP address from request headers
    '''
    try:
        # In FastAPI, we get forwarded IP from X-Forwarded-For header or client host
        # addresses = request.headers.get('X-Forwarded-For', request.client.host)
        # log.info(f'Client IP address: "{addresses}" at UTC: {datetime.utcnow()}')
        # client_ip = addresses.split(", ")[0]
        # ip_add = client_ip.replace("\\", "")
        # ip_addres = ip_add.replace("/", "")
        # ip_addresses = ip_addres.split(",")
        # log.info(f'Client IP addresses: "{ip_addresses}" at UTC: {datetime.utcnow()}')
        # client_ip_address = ip_addresses[0]
        # valid_ip = ip_address(client_ip_address).exploded
        # if do_logging:
        #     log.info(f'Client IP address: "{valid_ip}" at UTC: {datetime.utcnow()}')
        # return valid_ip
        return request.client.host
    except Exception as e:
        log.error(f'Error in getting client IP address: {e}')
        return None
