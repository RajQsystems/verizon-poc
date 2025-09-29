from fastapi import APIRouter
from pydantic import BaseModel

from agentic_ai import project_summary_generator
from agentic_ai.src.project_activities.schemas.flow.project_summary import ProjectSummaryResult

router = APIRouter(prefix="/common", tags=["Common"])


class ProjectSummaryRequest(BaseModel):
    project_id: str


@router.get("/summary/{project_id}", response_model=ProjectSummaryResult)
async def summarize_project(project_id: str):
    """
    Run the ProjectSummaryFlow (CrewAI pipeline) to analyze a project.
    """
    result = await project_summary_generator(project_id)
    return result
