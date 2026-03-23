from fastapi import APIRouter, HTTPException, Depends
from .service import UserService
from .schema import UserCreate, UserDeleteResponse, UserUpdate, UserOut
from ..auth.dependencies import require_admin

router = APIRouter()
service = UserService()

@router.get("/", response_model=list[UserOut])
async def list_users(admin=Depends(require_admin)):
    return await service.list_users()

@router.post("/", response_model=UserOut)
async def create_user(user: UserCreate, admin=Depends(require_admin)):
    await service.create_user(user.username, user.password, role="user", email=user.email)
    return UserOut(
        username=user.username, 
        role=user.role, 
        email=user.email
    )

@router.put("/{username}", response_model=UserOut)
async def update_user(username: str, user: UserUpdate, admin=Depends(require_admin)):
    try:
        await service.update_user(username, user.password, user.role, user.email)
        
        updated_user = await service.get_user(username)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found after update")
        
        return UserOut(
            username=updated_user["username"],
            role=updated_user["role"],
            email=updated_user.get("email")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{username}", response_model=UserDeleteResponse)
async def delete_user(username: str, admin=Depends(require_admin)):
    try:
        await service.delete_user(username)
        return UserDeleteResponse(
            status="deleted",
            username=username,
            message=f"User {username} deleted successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))