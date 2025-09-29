from pydantic import BaseModel
from typing import List, Optional

class Milestone(BaseModel):
    milestone_id: int
    name: str
    planned_date: Optional[str] = None
    actual_date: Optional[str] = None
    status: Optional[str] = None
    duration_days: Optional[int] = None
    description: Optional[str] = None

class Anomaly(BaseModel):
    anomaly_id: int
    milestone_id: int
    type: str
    severity: str
    description: Optional[str] = None
    detected_on: Optional[str] = None

class Cycle(BaseModel):
    cycle_id: int
    label: str
    agent_start_id: int
    agent_end_id: int
    planned: Optional[int] = None
    actual: Optional[int] = None
    variance: Optional[int] = None

class ProjectSummary(BaseModel):
    project: dict
    milestones: dict
    anomalies: dict
    cycles: List[Cycle]
