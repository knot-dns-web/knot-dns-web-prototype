from fastapi import APIRouter, HTTPException, Depends
from .service import UserService
from .schema import UserCreate, UserUpdate, UserOut
from ..auth.dependencies import require_admin

router = APIRouter()
service = UserService()

@router.get("/", response_model=list[UserOut])
def list_users(admin=Depends(require_admin)):
    return service.list_users()

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, admin=Depends(require_admin)):
    service.create_user(user.username, user.password, role="user", email=user.email)
    return {"username": user.username, "email": user.email}


@router.put("/{username}", response_model=UserOut)
def update_user(username: str, user: UserUpdate, admin=Depends(require_admin)):
    try:
        service.update_user(username, user.password, user.role, user.email)
        return {"status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{username}", response_model=UserOut)
def delete_user(username: str, admin=Depends(require_admin)):
    try:
        service.delete_user(username)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))