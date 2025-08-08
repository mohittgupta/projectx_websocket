import time

from config import logger

def timing_decorator(func):
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"{func.__name__} executed in {end - start:.6f} seconds")
        return result
    return wrapper