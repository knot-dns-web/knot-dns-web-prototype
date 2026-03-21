from typing import List

from fastapi import APIRouter, Depends

from ..auth.dependencies import get_current_user
from .schema import LogOut
from .service import LoggerService

router = APIRouter()
service = LoggerService()

@router.get("")
def get_logs(user: dict = Depends(get_current_user)):
    return {"logs": service.read_logs()}
