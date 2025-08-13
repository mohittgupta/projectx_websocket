import asyncio
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from signalrcore.hub_connection_builder import HubConnectionBuilder
import uvicorn
from config import logger, projectx_user_hubs
from db.crud_utils.login_central_utils.login_central_read_queries import get_by_user_id
from db.crud_utils.multi_user_connection_utils.multi_user_read_utils import get_multi_user_by_engine
from db.crud_utils.projectx_utils.projectx_orders_utils import get_projectx_order_by_order_id
from db.database import db_session
from db.models.projectx_data import Projectx_Orders
from project_utils import update_or_save_order_data, update_or_save_positions_data, update_or_save_trade_data
from mail_utils import send_email
import ssl
import websocket

app = FastAPI()

# Dictionary to store active SignalR connections by unique code
connections: Dict[str, 'UserSignalRClient'] = {}
connections_lock = asyncio.Lock()

class UserSignalRClient:
    def __init__(self, jwt_token: str, account_id: int, hub_url_base: str, unique_code: str, email: str = None):
        self.jwt_token = jwt_token
        self.account_id = account_id
        self.hub_url = f"{hub_url_base}?access_token={jwt_token}"
        self.unique_code = unique_code
        self.email = email
        self.hub_connection = None
        self.retry_count = 0
        self.max_retries = 3
        self.task = None
        self.loop = asyncio.get_running_loop()
        self.is_connecting = False
        self.setup_connection()

    def setup_connection(self):
        """Set up SignalR hub connection without automatic reconnect."""
        try:
            # Disable SSL verification for testing; remove in production
            websocket.enableTrace(False)
            self.hub_connection = HubConnectionBuilder()\
                .with_url(
                    self.hub_url,
                    options={
                        "access_token_factory": lambda: self.jwt_token,
                        "transport": "websockets",
                         # Temporary for debugging
                    })\
                .build()

            # Register event handlers (synchronous)
            logger.info(f"event subscribe done...")
            self.hub_connection.on("GatewayUserAccount", self.on_account_update)
            self.hub_connection.on("GatewayUserOrder", self.on_order_update)
            self.hub_connection.on("GatewayUserPosition", self.on_position_update)
            self.hub_connection.on("GatewayUserTrade", self.on_trade_update)
            self.hub_connection.on_open(self.on_connected)
            self.hub_connection.on_close(self.on_disconnected)
            self.hub_connection.on_error(self.on_error)
        except Exception as e:
            logger.error(f"Error setting up connection for {self.unique_code}: {e}")

    def on_account_update(self, args):
        logger.info(f"Account update for account {self.account_id} (code: {self.unique_code}): {args[0]} {args}")
        asyncio.run_coroutine_threadsafe(self._async_account_update(args), self.loop)

    def on_order_update(self, args):
        logger.info(f"Order update for account {self.account_id} (code: {self.unique_code}): {args[0]['data']}")
        asyncio.run_coroutine_threadsafe(self._async_order_update(args), self.loop)

    def on_position_update(self, args):
        logger.info(f"Position update for account {self.account_id} (code: {self.unique_code}): {args[0]}  {args}")
        asyncio.run_coroutine_threadsafe(self._async_position_update(args), self.loop)

    def on_trade_update(self, args):
        logger.info(f"Trade update for account {self.account_id} (code: {self.unique_code}): {args[0]}")
        asyncio.run_coroutine_threadsafe(self._async_trade_update(args), self.loop)

    def on_connected(self):
        logger.info(f"Connected to RTC Hub for account {self.account_id} (code: {self.unique_code})")
        asyncio.run_coroutine_threadsafe(self._async_connected(), self.loop)

    def on_disconnected(self):
        logger.info(f"Disconnected from account {self.account_id} (code: {self.unique_code})")
        asyncio.run_coroutine_threadsafe(self._async_disconnected(), self.loop)

    def on_error(self, error):
        logger.error(f"SignalR error for account {self.account_id} (code: {self.unique_code}): {error}")
        asyncio.run_coroutine_threadsafe(self._async_disconnected(), self.loop)

    async def _async_account_update(self, args):
        pass  # Add async logic if needed

    async def _async_order_update(self, args):
        asyncio.create_task(update_or_save_order_data(args[0]['data'], self.unique_code))

    async def _async_position_update(self, args):
        asyncio.create_task(update_or_save_positions_data(args[0]['data'], self.unique_code))

    async def _async_trade_update(self, args):
        asyncio.create_task(update_or_save_trade_data(args[0]['data'], self.unique_code))

    async def _async_connected(self):
        try:
            await self.subscribe_all()
            self.retry_count = 0
            self.is_connecting = False
            if self.email:
                await self.loop.run_in_executor(
                    None,
                    send_email,
                    self.email,
                    "ProjectX Account Connected",
                    "",
                    "Your account has been successfully connected to ProjectX.",
                    "connected"
                )
        except Exception as e:
            logger.error(f"Error in connected handler for {self.unique_code}: {e}")

    async def _async_disconnected(self):
        if self.is_connecting:
            return
        self.is_connecting = True
        self.retry_count += 1
        if self.retry_count <= self.max_retries:
            logger.info(f"Retrying connection {self.retry_count}/{self.max_retries} for account {self.account_id} (code: {self.unique_code})")
            await asyncio.sleep(5)
            try:
                self.hub_connection.stop()
                self.setup_connection()  # Rebuild connection to ensure clean state
                self.hub_connection.start()
            except Exception as e:
                logger.error(f"Retry attempt {self.retry_count} failed for account {self.account_id} (code: {self.unique_code}): {e}")
            finally:
                self.is_connecting = False
        else:
            logger.error(f"Max retries ({self.max_retries}) reached for account {self.account_id} (code: {self.unique_code})")
            if self.email:
                await self.loop.run_in_executor(
                    None,
                    send_email,
                    self.email,
                    "ProjectX Account Disconnected",
                    "",
                    f"Your account has been disconnected after {self.max_retries} unsuccessful retry attempts.",
                    "disconnect"
                )
            async with connections_lock:
                if self.unique_code in connections:
                    connections.pop(self.unique_code)
            self.is_connecting = False

    async def subscribe_all(self):
        try:
            self.hub_connection.send("SubscribeAccounts", [])
            self.hub_connection.send("SubscribeOrders", [self.account_id])
            self.hub_connection.send("SubscribePositions", [self.account_id])
            self.hub_connection.send("SubscribeTrades", [self.account_id])
        except Exception as e:
            logger.error(f"Error subscribing for account {self.account_id} (code: {self.unique_code}): {e}")

    async def unsubscribe_all(self):
        try:
            self.hub_connection.send("UnsubscribeAccounts", [])
            self.hub_connection.send("UnsubscribeOrders", [self.account_id])
            self.hub_connection.send("UnsubscribePositions", [self.account_id])
            self.hub_connection.send("UnsubscribeTrades", [self.account_id])
        except Exception as e:
            logger.error(f"Error unsubscribing for account {self.account_id} (code: {self.unique_code}): {e}")

    async def start(self):
        if self.is_connecting:
            return
        self.is_connecting = True
        try:
            self.hub_connection.start()
        except Exception as e:
            logger.error(f"Error during connection start for account {self.account_id} (code: {self.unique_code}): {e}")
            await self._async_disconnected()
        finally:
            self.is_connecting = False

    async def stop(self):
        try:
            self.is_connecting = True
            await self.unsubscribe_all()
            self.hub_connection.stop()
            if self.email:
                await self.loop.run_in_executor(
                    None,
                    send_email,
                    self.email,
                    "ProjectX Account Disconnected",
                    "",
                    "Your account has been manually disconnected.",
                    "disconnect"
                )
        except Exception as e:
            logger.error(f"Error stopping connection for {self.unique_code}: {e}")
        finally:
            self.is_connecting = False

class ConnectRequest(BaseModel):
    jwt_token: str
    account_id: int
    unique_code: str
    email: str
    websocket_url: str

@app.post("/connect")
async def connect(data: ConnectRequest):
    async with connections_lock:
        if data.unique_code in connections:
            raise HTTPException(status_code=409, detail=f"Connection with unique_code {data.unique_code} already exists")

        client = UserSignalRClient(
            jwt_token=data.jwt_token,
            account_id=data.account_id,
            hub_url_base=data.websocket_url,
            unique_code=data.unique_code,
            email=data.email
        )
        task = asyncio.create_task(client.start())
        connections[data.unique_code] = {"client": client, "task": task}
        logger.info(f"Started connection for unique_code {data.unique_code}")

    return {"message": f"Connection started for unique_code {data.unique_code}"}

@app.post("/disconnect/{unique_code}")
async def disconnect(unique_code: str):
    async with connections_lock:
        if unique_code not in connections:
            raise HTTPException(status_code=404, detail=f"No connection found for unique_code {unique_code}")

        client_info = connections.pop(unique_code)
        await client_info["client"].stop()
        client_info["task"].cancel()
        try:
            await client_info["task"]
        except asyncio.CancelledError:
            logger.info(f"Task cancelled for unique_code {unique_code}")
        logger.info(f"Stopped connection for unique_code {unique_code}")
        return {"message": f"Connection stopped for unique_code {unique_code}"}

@app.get("/connections")
async def list_connections():
    async with connections_lock:
        active_connections = [
            {
                "unique_code": code,
                "account_id": client_info["client"].account_id,
                "email": client_info["client"].email,
                "task_running": not client_info["task"].done()
            }
            for code, client_info in connections.items()
        ]
        return {"connections": active_connections}

@app.on_event("startup")
async def startup_event():
    # Launch your websocket task in the background
    asyncio.create_task(start_websocket_for_all())

# Use lifespan event handler instead of deprecated on_event
async def lifespan(app: FastAPI):
    yield  # Application startup
    # Shutdown cleanup
    async with connections_lock:
        for unique_code, client_info in list(connections.items()):
            await client_info["client"].stop()
            client_info["task"].cancel()
            try:
                await client_info["task"]
            except asyncio.CancelledError:
                logger.info(f"Task cancelled for unique_code {unique_code} during shutdown")
        connections.clear()

app.lifespan = lifespan

async def start_websocket_for_all():
    all_projectx_connections = get_multi_user_by_engine(engine="PROJECTX")
    for connection in all_projectx_connections:
        if connection.connection_datetime is None:
            logger.warning(f"Skipping connection {connection.id} due to missing connection_datetime")
            continue
        if connection.connection_datetime < (datetime.utcnow()- timedelta(days=1)):
            continue
        account_id_string = connection.connection_account_id
        account_id_data = json.loads(account_id_string)
        for account_name , account_id in account_id_data.items():
            user = get_by_user_id(connection.user_id)
            unique_code = f"{user.random_id}_{connection.connection_name}_{account_id}"
            hub_url = projectx_user_hubs.get(connection.connection_server)
            if unique_code not in connections:
                client = UserSignalRClient(
                    jwt_token=connection.connection_access_token,
                    account_id=account_id,
                    hub_url_base=hub_url,
                    unique_code=unique_code,
                    email=user.user_name
                )
                task = asyncio.create_task(client.start())
                async with connections_lock:
                    connections[unique_code] = {"client": client, "task": task}
                logger.info(f"Started connection for unique_code {unique_code}")

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=5030)