from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, case, select
from backend.app.dependencies.db import get_db
from backend.app.models.entities import Milestone, Agent, Project, CycleTime

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/agent/{agent_name}/delay-metrics")
async def agent_delay_metrics(agent_name: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(
            func.count(Milestone.milestone_id),
            func.avg(Milestone.duration_days),
            func.sum(case((Milestone.status == "Delayed", 1), else_=0)),
        )
        .join(Agent, Agent.agent_id == Milestone.agent_id)
        .filter(Agent.agent_name == agent_name)
    )

    result = await db.execute(stmt)
    total, avg_duration, delayed = result.one_or_none() or (0, None, 0)

    return {
        "agent": agent_name,
        "total_milestones": int(total or 0),
        "avg_duration_days": float(avg_duration) if avg_duration is not None else None,
        "delayed_milestones": int(delayed or 0),
    }


@router.get("/cycles/summary")
async def cycles_summary(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(CycleTime, Project.market)
        .join(Project, Project.project_id == CycleTime.project_id)
    )
    result = await db.execute(stmt)
    rows = result.all()

    data = {}
    for c, market in rows:
        key = getattr(c, "label", "cycle")  # fallback if no "label"
        data.setdefault(key, {"count": 0, "total_actual": 0, "by_market": {}})
        if c.actual_duration is not None:
            data[key]["count"] += 1
            data[key]["total_actual"] += c.actual_duration
            data[key]["by_market"].setdefault(market, {"count": 0, "total": 0})
            data[key]["by_market"][market]["count"] += 1
            data[key]["by_market"][market]["total"] += c.actual_duration

    out = []
    for label, v in data.items():
        avg = (v["total_actual"] / v["count"]) if v["count"] else None
        by_market = {
            m: round(d["total"] / d["count"], 2)
            for m, d in v["by_market"].items()
            if d["count"]
        }
        out.append({
            "label": label,
            "avg_actual_days": round(avg, 2) if avg else None,
            "by_market_avg": by_market,
        })

    return out
