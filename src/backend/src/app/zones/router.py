from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from ..auth.dependencies import get_current_user

from .service import ZoneService
from .schema import ZoneCreate, ZoneImport

router = APIRouter()

service = ZoneService()


@router.get("")
async def list_zones(user: dict = Depends(get_current_user)):
    return {"zones": await service.list_zones()}


@router.post("")
async def create_zone(zone: ZoneCreate, user: dict = Depends(get_current_user)):
    try:
        await service.create_zone(zone.name)
        return {"status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{zone_name}")
async def delete_zone(zone_name: str, user: dict = Depends(get_current_user)):
    try:
        await service.delete_zone(zone_name)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# @router.get("/{zone_name}/export", response_class=PlainTextResponse)
# def export_zone(zone_name: str):
#     try:
#         data = service.export_zone(zone_name)
#         return data
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=str(e))
    

from fastapi.responses import Response
@router.get("/{zone_name}/export")
async def export_zone(zone_name: str, user: dict = Depends(get_current_user)):
    try:
        data = await service.export_zone(zone_name)
        return Response(
            content=data,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={zone_name.rstrip('.')}.zone"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/import")
async def import_zone(zone: ZoneImport, user: dict = Depends(get_current_user)):
    try:
        await service.import_zone(zone.name, zone.content)
        return {"status": "imported"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))