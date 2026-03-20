from typing import List

from fastapi import APIRouter
from .schema import LogOut
from .service import LoggerService

router = APIRouter()
service = LoggerService()

@router.get("/")
def get_logs():
    return {"logs": service.read_logs()}
