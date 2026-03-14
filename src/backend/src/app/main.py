from fastapi import FastAPI

from .zones.router import router as zones_router
from .records.router import router as records_router
# from src.backend.src.app.auth.router import router as auth_router
from .users.router import router as users_router

# from ..knot_wrapper.example import start_processor
from ..knot_wrapper.transaction import set_knot_connection_path

import os
import threading


app = FastAPI(
    title="Knot DNS Manager",
    version="1.0.0"
)


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
# app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])


@app.get("/")
def root():
    return {"status": "Knot DNS API running"}