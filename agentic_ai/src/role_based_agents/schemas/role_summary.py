# backend/app/schemas/role_summary_schemas.py

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


# ----------------------------
# Core Entities
# ----------------------------
class StatusDistribution(BaseModel):
    status: str
    count: int


class Delay(BaseModel):
    project_id: str
    milestone: str
    planned_date: Optional[str] = None
    actual_date: Optional[str] = None
    delay_days: Optional[int] = None


class Anomaly(BaseModel):
    project_id: str
    type: str
    severity: str
    description: Optional[str] = None


class Impact(BaseModel):
    project_id: str
    vendor: Optional[str] = None
    delayed_milestones: int
    total_milestones: int


class Dependency(BaseModel):
    from_id: int
    to_id: int


# ----------------------------
# Debugging Structures
# ----------------------------
class AgentRun(BaseModel):
    task_key: str
    agent_key: str
    display_name: Optional[str] = None
    output_raw: Optional[str] = None
    output_json: Optional[Dict[str, Any]] = None
    task_details: Optional[Dict[str, Any]] = None
    agent_details: Optional[Dict[str, Any]] = None


# ----------------------------
# State During Execution
# ----------------------------
class RoleSummaryState(BaseModel):
    role: Optional[str] = None
    raw_role_summary: Optional[Dict[str, Any]] = None
    trace: List[Dict[str, Any]] = Field(default_factory=list)
    agents_debug: List[AgentRun] = Field(default_factory=list)


# ----------------------------
# Final Result (what frontend consumes)
# ----------------------------
class ActionItem(BaseModel):
    action: str

class RoleSummaryResult(BaseModel):
    role: str
    headline: str = ""
    risks: List[str] = []
    actions: List[ActionItem] = []   # 👈 allow dicts
    raw_output: Any = None
    trace: List[Dict[str, Any]] = Field(default_factory=list)
    agents: List[AgentRun] = Field(default_factory=list)



# ----------------------------
# Inputs/Outputs for tasks
# ----------------------------
class RoleSummaryInput(BaseModel):
    role: str


class RoleSummaryOutput(BaseModel):
    status: Dict[str, Any]
    delays: List[Delay]
    anomalies: List[Anomaly]
    impacts: List[Impact]
    dependencies: List[Dependency]
    final_summary: str
