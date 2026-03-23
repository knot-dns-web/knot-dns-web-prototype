from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

import os
import sys
import threading
import asyncio
import redis.asyncio as redis
from contextlib import asynccontextmanager

from .database import create_db_and_tables, init_db, get_async_session

from ..knot_wrapper.implementation.synchronous import *

from .zones.router import router as zones_router
from .records.router import router as records_router
from .auth.router import router as auth_router
from .users.router import router as users_router
from .logger.router import router as logger_router

from .middleware.logger import LoggingMiddleware

from ..knot_wrapper.implementation.asynchronous import DNSWorker
from .users.service import UserService

redis_client = redis.from_url("redis://redis:6379")
CHANNEL_NAME = "DNSCommitAsync"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    
    socket_path = os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")
    
    print("Starting application...")
    
    # Проверяем переменные окружения
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'not set')}")
    print(f"KNOT_SOCKET: {socket_path}")
    
    # Создаем таблицы с повторными попытками
    try:
        create_db_and_tables()
    except Exception as e:
        print(f"CRITICAL: Cannot connect to database: {e}")
        print("Exiting...")
        sys.exit(1)
    
    # Создаем админа если его нет
    try:
        async for session in get_async_session():
            try:
                service = UserService(session)
                admin = await service.get_user_by_username("admin")
                if not admin:
                    await service.create_user(
                        username="admin",
                        password="admin",
                        role="admin",
                        email="admin@example.com"
                    )
                    print("✅ Admin user created")
                else:
                    print("✅ Admin user already exists")
            except Exception as e:
                print(f"❌ Error creating admin: {e}")
            break
    except Exception as e:
        print(f"❌ Database session error: {e}")

    # Запускаем DNS worker
    try:
        print(f"Starting DNS worker with Redis at redis://redis:6379")
        worker = DNSWorker(redis_client, CHANNEL_NAME, socket_path)
        task = asyncio.create_task(worker.run())
        print("✅ DNS worker started")
    except Exception as e:
        print(f"❌ Failed to start DNS worker: {e}")
        task = None
    
    yield
    
    # Останавливаем worker
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    await redis_client.close()
    print("Application shutdown complete")



app = FastAPI(
    title="Knot DNS Manager",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(LoggingMiddleware, get_session=get_async_session)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


app.include_router(zones_router, prefix="/zones", tags=["zones"])
app.include_router(records_router, prefix="/records", tags=["records"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(logger_router, prefix="/logs", tags=["logs"])


@app.get("/")
def root():
    return {"status": "Knot DNS API running"}