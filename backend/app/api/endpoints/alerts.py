from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.dependencies.db import get_db
from backend.app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def get_alert_service(db: AsyncSession = Depends(get_db)) -> AlertService:
    return AlertService(db)


@router.get("", status_code=status.HTTP_200_OK)
async def get_alerts(service: AlertService = Depends(get_alert_service)):
    report = await service.get_full_report()
    return {"projects": report}
