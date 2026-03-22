from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth.dependencies import get_current_user
from .service import RecordService
from .schema import RecordCreate, RecordUpdate

router = APIRouter()

service = RecordService()

@router.get("")
def list_records(user: dict = Depends(get_current_user)):
    return {"records": service.list_records()}

@router.post("")
def create_record(record: RecordCreate, user: dict = Depends(get_current_user)):
    try:
        service.create_record(
            record.zone,
            record.owner,
            record.type,
            record.ttl,
            record.data
        )
        return {"status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{zone}")
def update_record(
    zone: str,
    body: RecordUpdate,
    user: dict = Depends(get_current_user),
):
    try:
        service.update_record(
            zone,
            body.old_owner,
            body.old_type,
            body.old_data,
            body.owner,
            body.type,
            body.ttl,
            body.data,
        )
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{zone}/{owner}/{rtype}")
def delete_record(
    zone: str,
    owner: str,
    rtype: str,
    data: str | None = Query(None),
    user: dict = Depends(get_current_user),
):
    try:
        service.delete_record(zone, owner, rtype, data)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))