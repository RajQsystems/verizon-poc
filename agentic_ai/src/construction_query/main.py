from decimal import Decimal
from datetime import datetime, timezone

import aiofiles
from crewai.flow import Flow, listen, start, router, or_
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from agentic_ai.src.construction_query.crews import (
    ConstructionResultInterpreterCrew,
    ConstructionQueryGeneratorCrew,
    ConstructionErrorUnderstandingCrew,
)
from agentic_ai.src.construction_query.schemas import ConstructionQueryState
from backend.app.db.session import AsyncSessionLocal


MAX_RETRIES = 3


class ConstructionQueryFlow(Flow[ConstructionQueryState]):
    @start()
    async def read_table_description(self):
        async with aiofiles.open("agentic_ai/data/data.txt", mode="r") as f:
            column_description = await f.read()
        self.state.column_description = column_description
        return column_description

    @listen(or_("read_table_description", "analyze_construction_error"))
    async def generate_construction_query(self, column_description):
        date_now = self._get_current_datetime()

        crew = ConstructionQueryGeneratorCrew()
        result = await crew.crew().kickoff_async(
            inputs={
                "column_description": column_description,
                "user_prompt": self.state.user_prompt,
                "date": date_now,
                "previous_error": self.state.previous_error_analysis,
            }
        )
        self.state.logical_query_plan = result.tasks_output[0].raw
        return result.raw

    @listen("generate_construction_query")
    async def run_construction_query(self, sql_query: str):
        if self.state.retry_count >= MAX_RETRIES:
            return "max_retries_exceeded"
        self.state.retry_count += 1

        try:
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    result = await session.execute(text(sql_query))
                    query_results_raw = [dict(row) for row in result.mappings().all()]

                    processed_results = []
                    for row in query_results_raw:
                        processed_row = {
                            key: float(value) if isinstance(value, Decimal) else value
                            for key, value in row.items()
                        }
                        processed_results.append(processed_row)

                    self.state.query_results = processed_results

            self.state.has_sql_error = False

        except SQLAlchemyError as e:
            self.state.previous_error.append(str(e))
            self.state.has_sql_error = True

    @router("run_construction_query")
    def handle_query_routing(self):
        if self.state.has_sql_error:
            return "analyze_error"
        return "interpret_construction_result"

    @listen("analyze_error")
    async def analyze_construction_error(self):
        crew = ConstructionErrorUnderstandingCrew()
        result = await crew.crew().kickoff_async(
            inputs={
                "user_prompt": self.state.user_prompt,
                "logical_query_plan": self.state.logical_query_plan,
                "previous_error": self.state.previous_error,
                "column_description": self.state.column_description,
            }
        )
        self.state.previous_error_analysis = result.json_dict or {}
        return result.json_dict

    @listen("interpret_construction_result")
    async def generate_construction_interpretation(self):
        crew = ConstructionResultInterpreterCrew()
        result = await crew.crew().kickoff_async(
            inputs={
                "user_prompt": self.state.user_prompt,
                "logical_query_plan": self.state.logical_query_plan,
                "query_results": self.state.query_results[:40],
                "column_description": self.state.column_description,
            }
        )
        output = result.json_dict
        if not output:
            return output
        output["data"].update({"rows": self.state.query_results})
        with open("construction_output.json", "w") as f:
            import json

            json.dump(output, f, indent=4)
        return output

    def _get_current_datetime(self):
        return datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M %Z")
