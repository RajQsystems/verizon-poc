from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.dependencies.db import get_db
from backend.app.models.entities import Agent, Milestone, Project, Anomaly
from backend.app.schemas.common import Agent as AgentSchema
from typing import List

router = APIRouter(prefix="/agents", tags=["Agents"])

# List agents
@router.get("/", response_model=List[AgentSchema])
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).order_by(Agent.agent_name.asc()))
    return result.scalars().all()

# Projects for an agent
@router.get("/{agent_name}/projects")
async def agent_projects(agent_name: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Project.project_id, Project.market, Project.site_type)
        .join(Milestone, Milestone.project_id == Project.project_id)
        .join(Agent, Agent.agent_id == Milestone.agent_id)
        .filter(Agent.agent_name == agent_name)
        .distinct()
    )
    result = await db.execute(stmt)
    return [{"project_id": r[0], "market": r[1], "site_type": r[2]} for r in result.all()]

# Anomalies for an agent
@router.get("/{agent_name}/anomalies")
async def agent_anomalies(agent_name: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Anomaly)
        .join(Milestone, Milestone.milestone_id == Anomaly.milestone_id)
        .join(Agent, Agent.agent_id == Milestone.agent_id)
        .filter(Agent.agent_name == agent_name)
    )
    result = await db.execute(stmt)
    anomalies = result.scalars().all()
    return [
        {
            "anomaly_id": a.anomaly_id,
            "milestone_id": a.milestone_id,
            "type": a.type,
            "severity": a.severity,
            "description": a.description,
            "detected_on": a.detected_on,
        }
        for a in anomalies
    ]
