from decimal import Decimal
from datetime import datetime, timezone

import aiofiles
from crewai.flow import Flow, listen, start, router, or_
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from agentic_ai.src.sql_query.crews import (
    SQLResultInterpreterCrew,
    SQLQueryGeneratorCrew,
)
from agentic_ai.src.sql_query.schemas import SQLQueryState
from backend.app.db.session import AsyncSessionLocal


MAX_RETRIES = 3


class SQLQueryGeneratorFlow(Flow[SQLQueryState]):
    @start()
    async def read_table_description(self):
        async with aiofiles.open("agentic_ai/data/data.txt", mode="r") as f:
            column_description = await f.read()
        self.state.column_description = column_description
        return column_description

    @listen(or_("read_table_description", "regenerate_sql_query"))
    async def generate_sql_query(self, column_description):
        date_now = self._get_current_datetime()

        crew = SQLQueryGeneratorCrew()
        result = await crew.crew().kickoff_async(
            inputs={
                "column_description": column_description,
                "user_prompt": self.state.user_prompt,
                "date": date_now,
                "previous_error": self.state.previous_error,
            }
        )
        self.state.logical_query_plan = result.tasks_output[0].raw
        return result.raw

    @router("generate_sql_query")
    async def handle_query_routing(self, sql_query: str):
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

            self.state.previous_error = None
            return "interpret_result"

        except SQLAlchemyError as e:
            self.state.previous_error = str(e)
            return "regenerate_sql_query"

    @listen("interpret_result")
    async def generate_sql_interpretation(self):
        crew = SQLResultInterpreterCrew()
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
        with open("output.json", "w") as f:
            import json

            json.dump(output, f, indent=4)
        return output

    @listen("max_retries_exceeded")
    def handle_max_retries(self):
        return {
            "error": "Maximum retry attempts exceeded. Please modify your prompt and try again."
        }

    def _get_current_datetime(self):
        return datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M %Z")
