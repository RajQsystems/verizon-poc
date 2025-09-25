from fastapi import FastAPI, APIRouter

from backend.app.api import init_routers


app = FastAPI(
    title="Agentic AI Boilerplate API",
    description="API for Agentic AI Boilerplate",
    version="1.0.0",
)
router = APIRouter(prefix="/api/v1")
init_routers(router)
app.include_router(router)
