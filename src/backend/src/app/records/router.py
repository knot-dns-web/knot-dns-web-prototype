from fastapi import APIRouter, HTTPException
from .service import RecordService
from .schema import RecordCreate

router = APIRouter()

service = RecordService()


@router.get("/")
def list_records():
    return {"records": service.list_records()}


@router.post("/")
def create_record(record: RecordCreate):
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
    

@router.delete("/")
def delete_record(zone: str, owner: str, rtype: str):
    try:
        service.delete_record(zone, owner, rtype)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))