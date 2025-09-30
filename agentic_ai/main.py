from agentic_ai.src.sql_query import SQLQueryGeneratorFlow
from agentic_ai.src.real_estate_query import RealEsateFlow
from agentic_ai.src.construction_query import ConstructionQueryFlow
from agentic_ai.src.project_activities import ProjectSummaryFlow
from agentic_ai.src.role_based_agents import RoleSummaryFlow  # ✅ add
from agentic_ai.exceptions import APIError
import json


async def sql_query_generator(user_prompt: str) -> None:
    try:
        flow = SQLQueryGeneratorFlow()
        result = await flow.kickoff_async(inputs={"user_prompt": user_prompt})
        return result
    except APIError:
        raise


async def real_estate_query(user_prompt: str) -> None:
    try:
        flow = RealEsateFlow()
        flow.plot("real_estate_flow")
    except APIError:
        raise


async def construction_query_generator(user_prompt: str) -> None:
    try:
        flow = ConstructionQueryFlow()
        flow.plot("construction_query_flow")
    except APIError:
        raise


async def project_summary_generator(project_id: str):
    """
    Kick off the ProjectSummaryFlow to analyze a project.
    """
    try:
        flow = ProjectSummaryFlow()
        result = await flow.kickoff_async(inputs={"project_id": project_id})
        return result
    except APIError as e:
        # Parse APIError message if it's JSON
        try:
            message = json.loads(e.message)
            detail = message.get("detail", e.message)
        except Exception:
            detail = e.message
        raise APIError(status_code=e.status_code, message=detail)


async def role_summary_generator(role: str):
    """
    Kick off the RoleSummaryFlow to analyze an agent role (status, delays, anomalies, etc.).
    """
    try:
        flow = RoleSummaryFlow()
        result = await flow.kickoff_async(inputs={"role": role})
        return result
    except APIError as e:
        try:
            message = json.loads(e.message)
            detail = message.get("detail", e.message)
        except Exception:
            detail = e.message
        raise APIError(status_code=e.status_code, message=detail)
