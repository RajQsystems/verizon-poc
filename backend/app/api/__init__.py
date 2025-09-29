from fastapi import APIRouter
from backend.app.api.endpoints.query import router as query_router
from backend.app.api.endpoints.alerts import router as alerts_router
from backend.app.api.endpoints.agents import router as agents_router
from backend.app.api.endpoints.analytics import router as analytics_router
from backend.app.api.endpoints.anomalies import router as anomalies_router
from backend.app.api.endpoints.projects import router as projects_router
from backend.app.api.endpoints.vendors import router as vendors_router
from backend.app.api.endpoints.common import router as common_router




def init_routers(router: APIRouter) -> None:
    router.include_router(query_router)
    router.include_router(alerts_router)
    router.include_router(agents_router)
    router.include_router(analytics_router)
    router.include_router(anomalies_router)
    router.include_router(projects_router)
    router.include_router(vendors_router)
    router.include_router(common_router)


__all__ = [
    "init_routers",
]
