from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.dependencies.db import get_db
from backend.app.models.entities import Anomaly, Milestone, Project, Agent

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


@router.get("/search")
async def search_anomalies(
    agent: str | None = None,
    project_id: str | None = None,
    market: str | None = None,
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Anomaly, Milestone, Project, Agent)
        .join(Milestone, Milestone.milestone_id == Anomaly.milestone_id)
        .join(Project, Project.project_id == Milestone.project_id)
        .join(Agent, Agent.agent_id == Milestone.agent_id)
    )

    if agent:
        stmt = stmt.filter(Agent.agent_name == agent)
    if project_id:
        stmt = stmt.filter(Project.project_id == project_id)
    if market:
        stmt = stmt.filter(Project.market == market)
    if severity:
        stmt = stmt.filter(Anomaly.severity == severity)

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "anomaly_id": a.anomaly_id,
            "project_id": p.project_id,
            "agent": ag.agent_name,
            "milestone_id": m.milestone_id,
            "milestone_name": m.milestone_name,
            "type": a.type,
            "severity": a.severity,
            "description": a.description,
            "detected_on": a.detected_on,
        }
        for (a, m, p, ag) in rows
    ]
