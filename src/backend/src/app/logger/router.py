from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth.dependencies import get_current_user, require_admin
from ..database import get_async_session
from .service import LoggerService
from .schema import LogOut

router = APIRouter()


@router.get("", response_model=list[LogOut])
async def get_logs(
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        service = LoggerService(session)
        logs = await service.read_logs()
        return logs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read logs: {str(e)}"
        )


# @router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
# async def clear_logs(
#     admin: dict = Depends(require_admin),
#     session: AsyncSession = Depends(get_async_session)
# ):
#     try:
#         service = LoggerService(session)
#         success = await service.clear_logs()
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to clear logs"
#             )
#         return None
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to clear logs: {str(e)}"
#         )