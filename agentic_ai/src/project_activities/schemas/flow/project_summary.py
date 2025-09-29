from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class AgentRun(BaseModel):
    task_key: str
    agent_key: str
    display_name: Optional[str] = None
    output_raw: Optional[str] = None
    output_json: Optional[Dict[str, Any]] = None
    task_details: Optional[Dict[str, Any]] = None   # 👈 add
    agent_details: Optional[Dict[str, Any]] = None  # 👈 add


class ProjectSummaryState(BaseModel):
    project_id: Optional[str] = None
    raw_project_summary: Optional[Dict[str, Any]] = None
    trace: List[Dict[str, Any]] = Field(default_factory=list)
    agents_debug: List[AgentRun] = Field(default_factory=list)   # 👈 NEW

class ProjectSummaryResult(BaseModel):
    project_id: str
    headline: str = ""
    risks: List[str] = []
    actions: List[str] = []
    raw_output: Any = None
    trace: List[Dict[str, Any]] = Field(default_factory=list)
    agents: List[AgentRun] = Field(default_factory=list)         # 👈 NEW



class ProjectSummaryInput(BaseModel):
    project_id: str


class ProjectSummaryOutput(BaseModel):
    overview: Dict[str, Any]
    milestone_analysis: Dict[str, Any]
    anomaly_analysis: Dict[str, Any]
    cycle_analysis: Dict[str, Any]
    final_summary: str
