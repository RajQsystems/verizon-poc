# agentic_ai/src/role_summary/flows/role_summary_flow.py

import json
import aiohttp
from datetime import datetime, timezone
from typing import List

from crewai.flow import Flow, listen, start
from agentic_ai.config.settings import settings
from agentic_ai.exceptions import APIError
from agentic_ai.src.role_based_agents.crews.role_summary import RoleSummaryCrew
from agentic_ai.src.role_based_agents.schemas.role_summary import RoleSummaryState, RoleSummaryResult, AgentRun
from agentic_ai.src.role_based_agents.schemas.role_summary import ActionItem

from agentic_ai.mapper import TASKS, AGENTS, TASK_TO_AGENT


def _ts():
    return datetime.now(timezone.utc).isoformat()


def _log(state: RoleSummaryState, step: str, message: str, payload=None):
    state.trace.append(
        {"time": _ts(), "step": step, "message": message, "payload": payload or {}}
    )


class RoleSummaryFlow(Flow[RoleSummaryState]):
    @start()
    async def fetch_role_summary(self):
        url = f"{settings.API_BASE_URL}/api/v1/alerts/{self.state.role}"
        _log(
            self.state,
            "fetch_role_summary:start",
            "Calling role summary endpoint",
            {"url": url},
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.text()
                if response.status != 200:
                    _log(
                        self.state,
                        "fetch_role_summary:error",
                        "Non-200 from backend",
                        {"status": response.status, "body": body},
                    )
                    raise APIError(status_code=response.status, message=body)

                data = await response.json()
                data.setdefault("role", self.state.role)
                self.state.raw_role_summary = data
                return data

    @listen("fetch_role_summary")
    async def run_role_summary_pipeline(self, overview):
        _log(self.state, "crew:start", "Starting RoleSummaryCrew")
        crew = RoleSummaryCrew()
        result = await crew.crew().kickoff_async(
            inputs={"role": self.state.role, "overview": overview}
        )

        runs: List[AgentRun] = []
        for idx, out in enumerate(getattr(result, "tasks_output", []) or []):
            task_key = getattr(out, "name", None) or f"task_{idx+1}"
            agent_key = TASK_TO_AGENT.get(task_key, f"agent_{idx+1}")

            runs.append(
                AgentRun(
                    task_key=task_key,
                    agent_key=agent_key,
                    display_name=f"{agent_key} — {task_key}",
                    output_raw=getattr(out, "raw", None),
                    output_json=getattr(out, "json_dict", None),
                    task_details=TASKS.get(task_key),
                    agent_details=AGENTS.get(agent_key),
                )
            )

        self.state.agents_debug = runs
        _log(self.state, "crew:done", "Crew finished", {"tasks": len(runs)})
        return getattr(result, "raw", result)

    @listen("run_role_summary_pipeline")
    async def complete_role_summary(self, previous_result) -> RoleSummaryResult:
        headline, risks, actions = "", [], []
        raw_text = (
            previous_result
            if isinstance(previous_result, str)
            else getattr(previous_result, "raw", str(previous_result))
        )

        try:
            parsed = getattr(previous_result, "json_dict", None) or json.loads(raw_text)
            headline = parsed.get("headline", "")
            risks = parsed.get("top_risks", [])

            # Ensure actions are ActionItem objects
            raw_actions = parsed.get("next_actions", [])
            actions = []
            for a in raw_actions:
                if isinstance(a, dict) and "action" in a:
                    actions.append(ActionItem(action=a["action"]))
                elif isinstance(a, str):
                    actions.append(ActionItem(action=a))

        except Exception:
            import re

            m_head = re.search(r"Headline:\s*(.*)", raw_text)
            headline = m_head.group(1).strip() if m_head else ""

            def _pull(title):
                m = re.search(title + r":\s*(.*?)\n\n", raw_text, re.S)
                return [
                    ln.strip("0123456789. ").strip()
                    for ln in (m.group(1).splitlines() if m else [])
                    if ln.strip()
                ]

            risks, raw_actions = _pull("Top 3 Risks"), _pull("Next 3 Actions")
            actions = [ActionItem(action=a) for a in raw_actions]

        return RoleSummaryResult(
            role=self.state.role or "",
            headline=headline,
            risks=risks,
            actions=actions,
            raw_output=raw_text,
            trace=self.state.trace,
            agents=self.state.agents_debug,
        )


# -------------------------------
# Entrypoint function
# -------------------------------
async def role_summary_generator(role: str) -> RoleSummaryResult:
    flow = RoleSummaryFlow()
    return await flow.kickoff_async(inputs={"role": role})
