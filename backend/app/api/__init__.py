from fastapi import APIRouter
from backend.app.api.endpoints.query import router as query_router


def init_routers(router: APIRouter) -> None:
    router.include_router(query_router)


__all__ = [
    "init_routers",
]
