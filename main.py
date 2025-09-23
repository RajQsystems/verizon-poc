from fastapi import FastAPI

from backend.app.api import init_routers


app = FastAPI(
    title="Agentic AI Boilerplate API",
    description="API for Agentic AI Boilerplate",
    version="1.0.0",
)
init_routers(app)
