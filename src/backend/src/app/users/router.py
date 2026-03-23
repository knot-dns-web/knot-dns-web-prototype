from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from .service import UserService
from .schema import UserCreate, UserUpdate, UserOut, UserDeleteResponse
from ..auth.dependencies import require_admin
from ..database import get_async_session

router = APIRouter()


@router.get("", response_model=List[UserOut])
async def list_users(
    admin: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        service = UserService(session)
        users = await service.list_users()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: dict = Depends(require_admin),  # или get_current_user если не только админ
    session: AsyncSession = Depends(get_async_session)
):
    try:
        service = UserService(session)
        username = current_user.get("sub")
        user = await service.get_user_by_username(username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserOut.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    admin: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        service = UserService(session)
        new_user = await service.create_user(
            username=user.username,
            password=user.password,
            role=user.role,
            email=user.email
        )
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{username}", response_model=UserOut)
async def update_user(
    username: str,
    user_update: UserUpdate,
    admin: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        service = UserService(session)
        updated_user = await service.update_user(
            username=username,
            password=user_update.password,
            email=user_update.email,
            role=user_update.role
        )
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{username}", response_model=UserDeleteResponse)
async def delete_user(
    username: str,
    admin: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session)
):
    #  if username == admin.get("sub"):
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Нельзя удалить самого себя",
    #     )
    try:
        service = UserService(session)
        await service.delete_user(username)
        
        return UserDeleteResponse(
            status="deleted",
            username=username,
            message=f"User {username} deleted successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )