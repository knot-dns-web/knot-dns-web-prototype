from pydantic import BaseModel


class ZoneCreate(BaseModel):
    name: str


class ZoneResponse(BaseModel):
    name: str


class ZoneImport(BaseModel):
    name: str
    content: str