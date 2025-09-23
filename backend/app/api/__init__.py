from fastapi import FastAPI
from backend.app.api.endpoints.users import router as users_router


def init_routers(app: FastAPI) -> None:
    app.include_router(users_router)


__all__ = [
    "init_routers",
]
