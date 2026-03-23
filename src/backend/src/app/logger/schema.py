from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Log(SQLModel, table=True):
    __tablename__ = "logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now().isoformat(), nullable=False)
    level: str = Field(nullable=False, index=True)
    message: str = Field(nullable=False)


class LogOut(SQLModel):
    id: int
    timestamp: datetime
    level: str
    message: str
    
    class Config:
        from_attributes = True