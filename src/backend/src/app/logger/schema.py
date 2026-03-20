from pydantic import BaseModel
from datetime import datetime


class LogOut(BaseModel):
    timestamp: datetime
    level: str
    message: str
    # user: str
    # action: str
    # details: str