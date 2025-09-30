# backend/app/api/routers/agents_router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from backend.app.dependencies.db import get_db
from backend.app.models.entities import (
    Project,
    Agent,
    Milestone,
    CycleTime,
    Anomaly,
    Dependency,
    Vendor,
    MilestoneVendor,
)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/{role}", status_code=status.HTTP_200_OK)
async def get_agent_summary(
    role: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Return a full summary for the given agent role (top 10 for each section):
    - status distribution
    - delays
    - anomalies
    - impacted projects
    - dependencies
    """

    # -------------------------------
    # STATUS
    # -------------------------------
    stmt_status = (
        select(Milestone.status, func.count(Milestone.milestone_id))
        .join(Project, Project.project_id == Milestone.project_id)
        .join(Agent, Agent.agent_id == Milestone.agent_id)
        .where(Agent.agent_name == role)
        .group_by(Milestone.status)
        .limit(10)
    )
    rows_status = (await db.execute(stmt_status)).all()
    status_distribution = [{"status": s, "count": c} for s, c in rows_status]

    # -------------------------------
    # DELAYS
    # -------------------------------
    stmt_delays = (
        select(
            Project.project_id,
            Milestone.milestone_name,
            Milestone.planned_date,
            Milestone.actual_date,
        )
        .join(Project, Project.project_id == Milestone.project_id)
        .join(Agent, Agent.agent_id == Milestone.agent_id)
        .where(Agent.agent_name == role)
        .limit(10)
    )
    rows_delays = (await db.execute(stmt_delays)).all()
    delays = []
    for pid, milestone_name, planned, actual in rows_delays:
        delay = (actual - planned).days if planned and actual else None
        delays.append({
            "project_id": pid,
            "milestone": milestone_name,
            "planned_date": planned,
            "actual_date": actual,
            "delay_days": delay,
        })

    # -------------------------------
    # ANOMALIES
    # -------------------------------
    stmt_anomalies = (
        select(Project.project_id, Anomaly.type, Anomaly.severity, Anomaly.description)
        .join(Milestone, Milestone.milestone_id == Anomaly.milestone_id)
        .join(Project, Project.project_id == Milestone.project_id)
        .join(Agent, Agent.agent_id == Milestone.agent_id)
        .where(Agent.agent_name == role)
        .limit(10)
    )
    rows_anomalies = (await db.execute(stmt_anomalies)).all()
    anomalies = [
        {"project_id": pid, "type": t, "severity": sev, "description": desc}
        for pid, t, sev, desc in rows_anomalies
    ]

    # -------------------------------
    # IMPACTS
    # -------------------------------
    stmt_impacts = (
        select(
            Project.project_id,
            Vendor.vendor_name,
            func.count(Milestone.milestone_id).filter(Milestone.status == "Delayed").label("delayed_count"),
            func.count(Milestone.milestone_id).label("total_count"),
        )
        .join(Milestone, Project.project_id == Milestone.project_id)
        .join(Agent, Agent.agent_id == Milestone.agent_id)
        .outerjoin(MilestoneVendor, MilestoneVendor.milestone_id == Milestone.milestone_id)
        .outerjoin(Vendor, Vendor.vendor_id == MilestoneVendor.vendor_id)
        .where(Agent.agent_name == role)
        .group_by(Project.project_id, Vendor.vendor_name)
        .limit(10)
    )
    rows_impacts = (await db.execute(stmt_impacts)).all()
    impacts = [
        {
            "project_id": pid,
            "vendor": vendor,
            "delayed_milestones": delayed,
            "total_milestones": total,
        }
        for pid, vendor, delayed, total in rows_impacts
    ]

    # -------------------------------
    # DEPENDENCIES
    # -------------------------------
    d = aliased(Dependency)
    stmt_dependencies = (
        select(d.prerequisite_id, d.milestone_id)
        .join(Milestone, Milestone.milestone_id == d.milestone_id)
        .join(Agent, Agent.agent_id == Milestone.agent_id)
        .where(Agent.agent_name == role)
        .limit(10)
    )
    rows_dependencies = (await db.execute(stmt_dependencies)).all()
    dependencies = [{"from": pre, "to": suc} for pre, suc in rows_dependencies]

    # -------------------------------
    # FINAL OUTPUT
    # -------------------------------
    return {
        "role": role,
        "status": {"distribution": status_distribution},
        "delays": delays,
        "anomalies": anomalies,
        "impacts": impacts,
        "dependencies": dependencies,
    }


# -------------------------------
# GET ALL AGENTS
# -------------------------------
@router.get("/agents/all", status_code=status.HTTP_200_OK)
async def list_agents(db: AsyncSession = Depends(get_db)):
    stmt = select(Agent.agent_id, Agent.agent_name, Agent.description)
    result = await db.execute(stmt)
    rows = result.all()

    return {
        "agents": [
            {"id": agent_id, "name": name, "description": desc}
            for agent_id, name, desc in rows
        ]
    }


# -------------------------------
# GET ALL MARKETS
# -------------------------------
@router.get("/markets", status_code=status.HTTP_200_OK)
async def list_markets(db: AsyncSession = Depends(get_db)):
    stmt = select(func.distinct(Project.market))
    result = await db.execute(stmt)
    rows = result.scalars().all()

    return {"markets": rows}



