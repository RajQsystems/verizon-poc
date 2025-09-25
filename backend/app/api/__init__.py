from fastapi import APIRouter
from backend.app.api.endpoints.query import router as query_router
from backend.app.api.endpoints.alerts import router as alerts_router


def init_routers(router: APIRouter) -> None:
    router.include_router(query_router)
    router.include_router(alerts_router)


__all__ = [
    "init_routers",
]
