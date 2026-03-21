from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

import os
import threading
import asyncio
import redis.asyncio as redis
from contextlib import asynccontextmanager

from ..knot_wrapper.implementation.synchronous import *
from ..knot_wrapper.transaction import set_knot_connection_path

from .zones.router import router as zones_router
from .records.router import router as records_router
from .auth.router import router as auth_router
from .users.router import router as users_router
from .logger.router import router as logger_router

from .middleware.logger import LoggingMiddleware

app = FastAPI(
    title="Knot DNS Manager",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

from ..knot_wrapper.implementation.asynchronous import DNSWorker

redis_client = redis.from_url("redis://redis:6379")
CHANNEL_NAME = "DNSCommitAsync"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    
    socket_path = os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")
    set_knot_connection_path(socket_path)

    user_service.create_user("admin", "admin", role="admin")

    worker = DNSWorker(redis_client, CHANNEL_NAME, socket_path)
    task = asyncio.create_task(worker.run())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await redis_client.close()

app = FastAPI(
    title="Knot DNS Manager",
    version="1.0.0",
    lifespan=lifespan
)

from .users.service import UserService
user_service = UserService()

app.include_router(zones_router, prefix="/zones", tags=["zones"])
app.include_router(records_router, prefix="/records", tags=["records"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(logger_router, prefix="/logs", tags=["logs"])


@app.get("/")
def root():
    return {"status": "Knot DNS API running"}