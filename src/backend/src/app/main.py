from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from ..knot_wrapper.implementation.synchronous import *
# from ..knot_wrapper.example import start_processor
from ..knot_wrapper.transaction import set_knot_connection_path

from .zones.router import router as zones_router
from .records.router import router as records_router
from .auth.router import router as auth_router
from .users.router import router as users_router
from .logger.router import router as logger_router


import os
import threading


from .middleware.logger import LoggingMiddleware

app = FastAPI(
    title="Knot DNS Manager",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@app.on_event("startup")
def startup():

    socket_path = os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")
    set_knot_connection_path(socket_path)

    # thread = threading.Thread(target=start_processor, daemon=True)
    # thread.start()


from .users.service import UserService
user_service = UserService()

@app.on_event("startup")
def create_default_admin():
    try:
        user_service.create_user("admin", "admin", role="admin")
    except:
        pass


app.include_router(zones_router, prefix="/zones", tags=["zones"])
app.include_router(records_router, prefix="/records", tags=["records"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(logger_router, prefix="/logs", tags=["logs"])


@app.get("/")
def root():
    return {"status": "Knot DNS API running"}