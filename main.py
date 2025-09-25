from contextlib import asynccontextmanager

import mlflow.crewai as mlflow_crewai
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from agentic_ai.config.langfuse import setup_langfuse
from backend.app.api import init_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_langfuse()

    mlflow_crewai.autolog()
    yield


app = FastAPI(
    title="Agentic AI Boilerplate API",
    description="API for Agentic AI Boilerplate",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1")
init_routers(router)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
