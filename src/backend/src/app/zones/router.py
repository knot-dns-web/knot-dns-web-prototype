from fastapi import APIRouter, HTTPException
from .service import ZoneService
from .schema import ZoneCreate

router = APIRouter()

service = ZoneService()


@router.get("/")
def list_zones():
    return {"zones": service.list_zones()}


@router.post("/")
def create_zone(zone: ZoneCreate):
    try:
        service.create_zone(zone.name)
        return {"status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{zone_name}")
def delete_zone(zone_name: str):
    try:
        service.delete_zone(zone_name)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))