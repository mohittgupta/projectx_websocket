import httpx
import asyncio

from config import logger


async def send_request(method, url, data=None, params=None, headers=None):
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            url,
            json=data,
            params=params,
            headers=headers if headers else None  # Add headers only if provided
        )
        logger.info(f"Response for request {url} : {response.text}")
        print(f"Response for request {url} : {response.text}")
        return response