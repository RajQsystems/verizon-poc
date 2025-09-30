from fastapi import APIRouter
from pydantic import BaseModel

from agentic_ai import project_summary_generator, role_summary_generator
from agentic_ai.src.project_activities.schemas.flow.project_summary import ProjectSummaryResult
from agentic_ai.src.role_based_agents.schemas.role_summary import RoleSummaryResult


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

@router.get("/role/summary/{role}", response_model=RoleSummaryResult)
async def summarize_role(role: str):
    """
    Run the RoleSummaryFlow (CrewAI pipeline) to analyze a role (status, delays, anomalies, etc.).
    """
    result = await role_summary_generator(role)
    return result
