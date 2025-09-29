import json
import aiohttp
from datetime import datetime, timezone
from typing import List

from crewai.flow import Flow, listen, start
from agentic_ai.config.settings import settings
from agentic_ai.exceptions import APIError
from agentic_ai.src.project_activities.crews.project_summary.project_summary_crew import ProjectSummaryCrew
from agentic_ai.src.project_activities.schemas.flow.project_summary import (
    ProjectSummaryState, ProjectSummaryResult, AgentRun
)
from agentic_ai.mapper import TASKS, AGENTS, TASK_TO_AGENT

def _ts(): return datetime.now(timezone.utc).isoformat()

def _log(state: ProjectSummaryState, step: str, message: str, payload=None):
    state.trace.append({"time": _ts(), "step": step, "message": message, "payload": payload or {}})

class ProjectSummaryFlow(Flow[ProjectSummaryState]):
    @start()
    async def fetch_project_summary(self):
        url = f"{settings.API_BASE_URL}/api/v1/projects/{self.state.project_id}/summary"
        _log(self.state, "fetch_project_summary:start", "Calling project summary endpoint", {"url": url})

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.text()
                if response.status != 200:
                    _log(self.state, "fetch_project_summary:error", "Non-200 from backend",
                         {"status": response.status, "body": body})
                    raise APIError(status_code=response.status, message=body)

                data = await response.json()
                data.setdefault("project_id", self.state.project_id)
                self.state.raw_project_summary = data
                return data

    @listen("fetch_project_summary")
    async def run_project_summary_pipeline(self, overview):
        _log(self.state, "crew:start", "Starting ProjectSummaryCrew")
        crew = ProjectSummaryCrew()
        result = await crew.crew().kickoff_async(
            inputs={"project_id": self.state.project_id, "overview": overview}
        )

        runs: List[AgentRun] = []
        for idx, out in enumerate(getattr(result, "tasks_output", []) or []):
            task_key = getattr(out, "name", None) or f"task_{idx+1}"
            agent_key = TASK_TO_AGENT.get(task_key, f"agent_{idx+1}")

            runs.append(AgentRun(
                task_key=task_key,
                agent_key=agent_key,
                display_name=f"{agent_key} — {task_key}",
                output_raw=getattr(out, "raw", None),
                output_json=getattr(out, "json_dict", None),
                task_details=TASKS.get(task_key),
                agent_details=AGENTS.get(agent_key),
            ))

        self.state.agents_debug = runs
        _log(self.state, "crew:done", "Crew finished", {"tasks": len(runs)})
        return getattr(result, "raw", result)

    @listen("run_project_summary_pipeline")
    async def complete_project_summary(self, previous_result) -> ProjectSummaryResult:
        headline, risks, actions = "", [], []
        raw_text = previous_result if isinstance(previous_result, str) else getattr(previous_result, "raw", str(previous_result))

        try:
            parsed = getattr(previous_result, "json_dict", None) or json.loads(raw_text)
            headline = parsed.get("headline", "")
            risks = parsed.get("top_risks", [])
            actions = parsed.get("next_actions", [])
        except Exception:
            import re
            m_head = re.search(r"Headline:\s*(.*)", raw_text)
            headline = (m_head.group(1).strip() if m_head else "")
            def _pull(title):
                m = re.search(title + r":\s*(.*?)\n\n", raw_text, re.S)
                return [ln.strip("0123456789. ").strip() for ln in (m.group(1).splitlines() if m else []) if ln.strip()]
            risks, actions = _pull("Top 3 Risks"), _pull("Next 3 Actions")

        return ProjectSummaryResult(
            project_id=self.state.project_id,
            headline=headline,
            risks=risks,
            actions=actions,
            raw_output=raw_text,
            trace=self.state.trace,
            agents=self.state.agents_debug,
        )

async def project_summary_generator(project_id: str) -> ProjectSummaryResult:
    flow = ProjectSummaryFlow()
    return await flow.kickoff_async(inputs={"project_id": project_id})
