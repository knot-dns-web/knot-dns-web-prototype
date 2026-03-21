from fastapi import APIRouter, HTTPException
from .service import RecordService
from .schema import RecordCreate

router = APIRouter()

service = RecordService()


@router.get("/")
async def list_records():
    return {"records": await service.list_records()}


@router.post("/")
async def create_record(record: RecordCreate):
    try:
        await service.create_record(
            record.zone,
            record.owner,
            record.type,
            record.ttl,
            record.data
        )
        return {"status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.delete("/{zone}/{owner}/{rtype}")
async def delete_record(zone: str, owner: str, rtype: str):
    try:
        await service.delete_record(zone, owner, rtype)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))