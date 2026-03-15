from pydantic import BaseModel


class RecordCreate(BaseModel):
    zone: str
    owner: str
    type: str
    ttl: int
    data: str