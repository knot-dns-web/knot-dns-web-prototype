from fastapi import HTTPException, Header
from ..users.service import UserService

service = UserService()

def require_admin(x_user: str = Header(...)):
    # пока авторизация через header X-User (потом перейдём на JWT)

    user = service.get_user(x_user)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin required")

    return user