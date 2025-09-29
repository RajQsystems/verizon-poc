from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.dependencies.db import get_db
from backend.app.models.entities import Project, Milestone, Anomaly, CycleTime
from backend.app.schemas.common import Project as ProjectSchema, Milestone as MilestoneSchema, Anomaly as AnomalySchema, CycleTime as CycleSchema
from typing import List, Dict

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).filter(Project.project_id == project_id))
    p = result.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p


@router.get("/{project_id}/timeline", response_model=Dict[str, List[MilestoneSchema]])
async def project_timeline(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Milestone).filter(Milestone.project_id == project_id).order_by(Milestone.planned_date.asc())
    )
    ms = result.scalars().all()
    if not ms:
        raise HTTPException(status_code=404, detail="No milestones for project")
    return {"milestones": ms}


@router.get("/{project_id}/anomalies", response_model=List[AnomalySchema])
async def project_anomalies(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Anomaly)
        .join(Milestone, Milestone.milestone_id == Anomaly.milestone_id)
        .filter(Milestone.project_id == project_id)
        .order_by(Anomaly.detected_on.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{project_id}/cycles", response_model=List[CycleSchema])
async def project_cycles(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CycleTime).filter(CycleTime.project_id == project_id))
    return result.scalars().all()


@router.get("/{project_id}/summary")
async def project_summary(project_id: str, db: AsyncSession = Depends(get_db)):
    # 1. Project
    result = await db.execute(select(Project).filter(Project.project_id == project_id))
    p = result.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Milestones (with healthy vs delayed split + descriptions)
    result = await db.execute(
        select(Milestone).filter(Milestone.project_id == project_id).order_by(Milestone.planned_date.asc())
    )
    milestones = result.scalars().all()

    healthy_ms = []
    delayed_ms = []
    for m in milestones:
        ms_json = {
            "milestone_id": m.milestone_id,
            "name": m.milestone_name,
            "planned_date": str(m.planned_date) if m.planned_date else None,
            "actual_date": str(m.actual_date) if m.actual_date else None,
            "status": m.status,
            "duration_days": m.duration_days,
            "description": f"{m.milestone_name} for {p.market}",  # placeholder; replace with actual description if needed
        }
        if m.status == "Delayed":
            delayed_ms.append(ms_json)
        else:
            healthy_ms.append(ms_json)

    # 3. Anomalies (full details)
    stmt = (
        select(Anomaly)
        .join(Milestone, Milestone.milestone_id == Anomaly.milestone_id)
        .filter(Milestone.project_id == project_id)
        .order_by(Anomaly.detected_on.desc())
    )
    result = await db.execute(stmt)
    anomalies = [
        {
            "anomaly_id": a.anomaly_id,
            "milestone_id": a.milestone_id,
            "type": a.type,
            "severity": a.severity,
            "description": a.description,
            "detected_on": str(a.detected_on) if a.detected_on else None,
        }
        for a in result.scalars().all()
    ]

    # 4. Cycles (full details)
    result = await db.execute(select(CycleTime).filter(CycleTime.project_id == project_id))
    cycles = [
        {
            "cycle_id": c.cycle_id,
            "label": getattr(c, "label", "cycle"),
            "agent_start_id": c.agent_start_id,
            "agent_end_id": c.agent_end_id,
            "planned": c.planned_duration,
            "actual": c.actual_duration,
            "variance": c.variance,
        }
        for c in result.scalars().all()
    ]

    # Final structured response
    return {
        "project": {
            "project_id": p.project_id,
            "market": p.market,
            "site_type": p.site_type,
            "start_date": str(p.start_date) if p.start_date else None,
            "end_date_planned": str(p.end_date_planned) if p.end_date_planned else None,
            "end_date_actual": str(p.end_date_actual) if p.end_date_actual else None,
        },
        "milestones": {
            "total": len(milestones),
            "delayed": len(delayed_ms),
            "healthy_milestones": healthy_ms,
            "delayed_milestones": delayed_ms,
        },
        "anomalies": {
            "count": len(anomalies),
            "details": anomalies,
        },
        "cycles": cycles,
    }
