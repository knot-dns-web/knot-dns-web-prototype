from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"   # по умолчанию обычный пользователь
    email: Optional[str] = None


class UserUpdate(BaseModel):
    username: str
    password: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class UserOut(BaseModel):
    username: str
    role: str
    email: Optional[str] = None

class UserDeleteResponse(BaseModel):
    status: str
    username: str
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"