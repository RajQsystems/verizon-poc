from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.dependencies.db import get_db
from backend.app.models.entities import Vendor, MilestoneVendor, Milestone, Project

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("/top-delays")
async def vendors_top_delays(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Vendor.vendor_name, Project.market, Project.site_type)
        .join(MilestoneVendor, MilestoneVendor.vendor_id == Vendor.vendor_id)
        .join(Milestone, Milestone.milestone_id == MilestoneVendor.milestone_id)
        .join(Project, Project.project_id == Milestone.project_id)
        .filter(Milestone.status == "Delayed")
    )

    result = await db.execute(stmt)
    rows = result.all()

    counts = {}
    for vendor_name, market, site_type in rows:
        counts.setdefault(vendor_name, 0)
        counts[vendor_name] += 1

    return [
        {"vendor": k, "delayed_milestones": v}
        for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)
    ]
