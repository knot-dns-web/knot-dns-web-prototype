from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from .service import ZoneService
from .schema import ZoneCreate, ZoneImport

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


# @router.get("/{zone_name}/export", response_class=PlainTextResponse)
# def export_zone(zone_name: str):
#     try:
#         data = service.export_zone(zone_name)
#         return data
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=str(e))
    

from fastapi.responses import Response
@router.get("/{zone_name}/export")
def export_zone(zone_name: str):
    try:
        data = service.export_zone(zone_name)
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
def import_zone(zone: ZoneImport):
    try:
        service.import_zone(zone.name, zone.content)
        return {"status": "imported"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))