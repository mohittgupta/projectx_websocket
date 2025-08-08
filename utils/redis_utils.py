'''
'''
import redis

redis_client = redis.ConnectionPool(host="127.0.0.1", port=6379, db=10, decode_responses=True)

#NEED to add env variables for redis host, port, username, password

redis_connection_pool = redis_client



