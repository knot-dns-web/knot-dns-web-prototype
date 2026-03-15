from fastapi import APIRouter, HTTPException, Depends
from .service import UserService
from .schema import UserCreate, UserUpdate
from ..auth.dependencies import require_admin

router = APIRouter()
service = UserService()


@router.get("/", dependencies=[Depends(require_admin)])
def list_users():
    return {"users": service.list_users()}


@router.post("/", dependencies=[Depends(require_admin)])
def create_user(user: UserCreate):
    try:
        service.create_user(user.username, user.password, user.role, user.email)
        return {"status": "created"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{username}", dependencies=[Depends(require_admin)])
def update_user(username: str, user: UserUpdate):
    try:
        service.update_user(username, user.password, user.role, user.email)
        return {"status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{username}", dependencies=[Depends(require_admin)])
def delete_user(username: str):
    try:
        service.delete_user(username)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))