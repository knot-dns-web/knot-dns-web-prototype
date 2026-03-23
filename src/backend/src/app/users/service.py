from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from typing import Optional, List
from .schema import User, UserOut
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def list_users(self) -> List[UserOut]:
        try:
            stmt = select(User)
            result = await self.session.execute(stmt)
            users = result.scalars().all()
            return [UserOut.model_validate(user) for user in users]
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_user(
        self, 
        username: str, 
        password: str, 
        role: str = "user", 
        email: Optional[str] = None
    ) -> UserOut:
        # Проверяем существование пользователя
        existing = await self.get_user_by_username(username)
        if existing:
            raise ValueError(f"User {username} already exists")
        
        if email:
            existing_email = await self.get_user_by_email(email)
            if existing_email:
                raise ValueError(f"Email {email} already registered")
        
        # Хэшируем пароль
        hashed_password = pwd_context.hash(password)
        
        # Создаем пользователя
        user = User(
            username=username,
            hashed_password=hashed_password,
            role=role,
            email=email
        )
        
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        await self.session.commit() 
        
        return UserOut.model_validate(user)
    
    async def update_user(
        self,
        username: str,
        password: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None
    ) -> UserOut:
        user = await self.get_user_by_username(username)
        if not user:
            raise ValueError(f"User {username} not found")
        
        # Проверяем email на уникальность
        if email and email != user.email:
            existing_email = await self.get_user_by_email(email)
            if existing_email:
                raise ValueError(f"Email {email} already registered")
            user.email = email
        
        # Обновляем поля
        if password:
            user.hashed_password = pwd_context.hash(password)
        if role:
            user.role = role
        
        await self.session.flush()
        await self.session.refresh(user)
        
        return UserOut.model_validate(user)
    
    async def delete_user(self, username: str) -> bool:
        user = await self.get_user_by_username(username)
        if not user:
            raise ValueError(f"User {username} not found")
        
        await self.session.delete(user)
        await self.session.flush()
        return True
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = await self.get_user_by_username(username)
        if not user:
            print(f"User {username} not found")
            return None
        
        print(f"Verifying password for {username}")
        print(f"Password provided: {password}") 
        print(f"Hashed password in DB: {user.hashed_password}")
        
        if not pwd_context.verify(password, user.hashed_password):
            print("Password verification failed") 
            return None
        
        print("Password verified successfully") 
        return user