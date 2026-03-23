from typing import Optional
from pydantic import BaseModel

class RecordCreate(BaseModel):
    zone: str
    owner: str
    type: str
    ttl: int
    data: str

class RecordUpdate(BaseModel):
    old_owner: str
    old_type: str
    old_data: Optional[str] = None
    owner: str
    type: str
    ttl: int
    data: str