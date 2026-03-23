from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, nullable=False)
    email: Optional[str] = Field(default=None, unique=True, index=True)
    hashed_password: str = Field(nullable=False)
    role: str = Field(default="user", nullable=False)


class UserCreate(SQLModel):
    username: str
    password: str
    role: str = "user"
    email: Optional[str] = None


class UserUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class UserOut(SQLModel):
    id: int
    username: str
    role: str
    email: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserDeleteResponse(SQLModel):
    status: str
    username: str
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"