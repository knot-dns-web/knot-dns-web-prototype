from fastapi import APIRouter, HTTPException
from .service import ZoneService
from .schema import ZoneCreate

router = APIRouter()

service = ZoneService()


@router.get("")
async def list_zones():
    return {"zones": await service.list_zones()}


@router.post("")
async def create_zone(zone: ZoneCreate):
    try:
        await service.create_zone(zone.name)
        return {"status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{zone_name}")
async def delete_zone(zone_name: str):
    try:
        await service.delete_zone(zone_name)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))