import json
import aiohttp

from crewai.flow import Flow, listen, start

from agentic_ai.config.settings import settings
from agentic_ai.exceptions import APIError
from agentic_ai.src.project_activities.crews.project_summary.project_summary_crew import ProjectSummaryCrew
from agentic_ai.src.project_activities.schemas.flow.project_summary import (
    ProjectSummaryState,
    ProjectSummaryResult,
)
import re


class ProjectSummaryFlow(Flow[ProjectSummaryState]):
    @start()
    async def fetch_project_summary(self):
        """
        Fetch raw project summary JSON from the backend API.
        """
        url = f"{settings.API_BASE_URL}/api/v1/projects/{self.state.project_id}/summary"
        print("url_value ",url)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.text()
                if response.status != 200:
                    raise APIError(status_code=response.status, message=body)

                data = await response.json()

                # Always inject project_id so schema validation passes
                data.setdefault("project_id", self.state.project_id)

                # Save raw JSON into state for downstream steps
                self.state.raw_project_summary = data
                print("raw_data_008", data)
                return data

    @listen("fetch_project_summary")
    async def run_project_summary_pipeline(self, previous_result):
        """
        Pass the raw project summary into the Crew pipeline for analysis.
        """
        crew = ProjectSummaryCrew()
        print('crewcrew',crew)
        result = await crew.crew().kickoff_async(
            inputs={
                "project_id": self.state.project_id,
                "overview": previous_result,
            }
        )
        # crew result is usually a JSON-like string
        return result.raw


    @listen("run_project_summary_pipeline")
    async def complete_project_summary(self, previous_result: str) -> ProjectSummaryResult:
        try:
            parsed = json.loads(previous_result)
            headline = parsed.get("headline", "")
            risks = parsed.get("top_risks", [])
            actions = parsed.get("next_actions", [])
        except Exception:
            # Fallback: regex parse
            headline_match = re.search(r"Headline:\s*(.*)", previous_result)
            risks_block = re.search(r"Top 3 Risks:\s*(.*?)\n\n", previous_result, re.S)
            actions_block = re.search(r"Next 3 Actions:\s*(.*?)\n\n", previous_result, re.S)

            headline = headline_match.group(1).strip() if headline_match else ""
            risks = [line.strip("0123456789. ") for line in (risks_block.group(1).splitlines() if risks_block else []) if line.strip()]
            actions = [line.strip("0123456789. ") for line in (actions_block.group(1).splitlines() if actions_block else []) if line.strip()]

        return ProjectSummaryResult(
            project_id=self.state.project_id,
            headline=headline,
            risks=risks,
            actions=actions,
            raw_output=previous_result,
        )



async def project_summary_generator(project_id: str) -> ProjectSummaryResult:
    """
    Kick off the ProjectSummaryFlow and return a ProjectSummaryResult.
    """
    flow = ProjectSummaryFlow()
    result: ProjectSummaryResult = await flow.kickoff_async(
        inputs={"project_id": project_id}
    )
    return result


# For manual testing
if __name__ == "__main__":
    import asyncio

    async def main():
        project_id = "ID_SAMPLE_PROJECT"
        result = await project_summary_generator(project_id)
        print(result)

    asyncio.run(main())
