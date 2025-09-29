from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ProjectSummaryState(BaseModel):
    project_id: Optional[str] = None
    raw_project_summary: Optional[Dict[str, Any]] = None
    


class ProjectSummaryResult(BaseModel):
    """Final structured result from the crew."""
    project_id: str
    headline: str
    risks: List[str]
    actions: List[str]
    raw_output: Any


class ProjectSummaryInput(BaseModel):
    project_id: str


class ProjectSummaryOutput(BaseModel):
    overview: Dict[str, Any]
    milestone_analysis: Dict[str, Any]
    anomaly_analysis: Dict[str, Any]
    cycle_analysis: Dict[str, Any]
    final_summary: str
