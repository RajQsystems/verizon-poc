from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ProjectBase(BaseModel):
    project_id: str
    market: str
    site_type: Optional[str] = None


class Project(ProjectBase):
    start_date: Optional[date] = None
    end_date_planned: Optional[date] = None
    end_date_actual: Optional[date] = None

    class Config:
        orm_mode = True


class Agent(BaseModel):
    agent_id: int
    agent_name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class Milestone(BaseModel):
    milestone_id: int
    project_id: str
    agent_id: int
    milestone_name: str
    planned_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: Optional[str] = None
    duration_days: Optional[int] = None
    anomaly_flag: Optional[bool] = False

    class Config:
        orm_mode = True


class Anomaly(BaseModel):
    anomaly_id: int
    milestone_id: int
    type: str
    description: Optional[str] = None
    severity: Optional[str] = None
    detected_on: Optional[datetime] = None

    class Config:
        orm_mode = True


class CycleTime(BaseModel):
    cycle_id: int
    project_id: str
    agent_start_id: int
    agent_end_id: int
    planned_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    variance: Optional[int] = None

    class Config:
        orm_mode = True
