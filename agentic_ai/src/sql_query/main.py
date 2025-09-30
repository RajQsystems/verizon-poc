from decimal import Decimal
from datetime import datetime, timezone
import aiofiles

from crewai.flow import Flow, listen, start, router, or_
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from agentic_ai.src.sql_query.crews import (
    SQLResultInterpreterCrew,
    SQLQueryGeneratorCrew,
    SQLErrorUnderstandingCrew,
)
from agentic_ai.src.sql_query.schemas import SQLQueryState
from backend.app.db.session import AsyncSessionLocal


MAX_RETRIES = 5


class SQLQueryGeneratorFlow(Flow[SQLQueryState]):
    # -----------------------------
    # Internal helpers
    # -----------------------------
    def _now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")

    def _trace(self, step: str, message: str = "", payload: dict | None = None):
        """Append a debug trace step into state.execution_trace if present"""
        if hasattr(self.state, "execution_trace"):
            self.state.execution_trace.append(
                {
                    "time": self._now(),
                    "step": step,
                    "message": message,
                    "payload": payload or {},
                }
            )

    def _get_current_datetime(self):
        return datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M %Z")

    # -----------------------------
    # 1) Read schema description
    # -----------------------------
    @start()
    async def read_table_description(self):
        self.state.retry_count = 0
        async with aiofiles.open("agentic_ai/data/data.txt", mode="r") as f:
            column_description = await f.read()
        self.state.column_description = column_description
        self._trace("read_table_description", "Loaded schema description.", {
            "chars": len(column_description)
        })
        return column_description

    # -----------------------------
    # 2) Generate SQL
    # -----------------------------
    @listen(or_("read_table_description", "analyze_sql_error"))
    async def generate_sql_query(self, column_description):
        date_now = self._get_current_datetime()

        crew = SQLQueryGeneratorCrew()
        result = await crew.crew().kickoff_async(
            inputs={
                "column_description": column_description,
                "user_prompt": self.state.user_prompt,
                "date": date_now,
                "previous_error": self.state.previous_error_analysis,
            }
        )

        self.state.logical_query_plan = result.tasks_output[0].raw or ""
        self.state.sql_query = result.raw or ""   # ensure not None

        self._trace("generate_sql_query", "Generated SQL query.", {
            "logical_plan_preview": self.state.logical_query_plan[:200],
            "sql_query": self.state.sql_query,
        })
        return self.state.sql_query

    # -----------------------------
    # 3) Run SQL
    # -----------------------------
    @listen("generate_sql_query")
    async def run_sql_query(self, sql_query: str):
        try:
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    result = await session.execute(text(sql_query))
                    query_results_raw = [dict(row) for row in result.mappings().all()]

                    processed_results = []
                    for row in query_results_raw:
                        processed_results.append({
                            key: (
                                float(value) if isinstance(value, Decimal)
                                else value.isoformat() if hasattr(value, "isoformat")
                                else value
                            )
                            for key, value in row.items()
                        })

                    self.state.query_results = processed_results or []

            self.state.has_sql_error = False
            self.state.empty_result = not bool(self.state.query_results)

            self._trace("run_sql_query", "Executed SQL successfully.", {
                "row_count": len(self.state.query_results),
                "sample": self.state.query_results[:3],
            })

        except SQLAlchemyError as e:
            self.state.previous_error.append(str(e))
            self.state.has_sql_error = True
            self.state.query_results = []
            self.state.empty_result = True

            self._trace("run_sql_query", "SQL execution failed.", {
                "error": str(e),
                "sql_query": sql_query,
            })

    # -----------------------------
    # 4) Route next step
    # -----------------------------
    @router("run_sql_query")
    def handle_query_routing(self):
        if self.state.retry_count >= MAX_RETRIES:
            return "max_retries_exceeded"
        self.state.retry_count += 1

        if self.state.has_sql_error:
            return "analyze_sql_error"
        if getattr(self.state, "empty_result", False):
            return "interpret_result"   # still interpret even if empty
        return "interpret_result"

    # -----------------------------
    # 5) Error Analysis
    # -----------------------------
    @listen("analyze_error")
    async def analyze_sql_error(self):
        crew = SQLErrorUnderstandingCrew()
        date_now = self._get_current_datetime()
        result = await crew.crew().kickoff_async(
            inputs={
                "user_prompt": self.state.user_prompt,
                "logical_query_plan": self.state.logical_query_plan,
                "previous_error": self.state.previous_error,
                "column_description": self.state.column_description,
                "date": date_now,
            }
        )
        self.state.previous_error_analysis = result.json_dict or {}
        self._trace("analyze_sql_error", "Analyzed SQL error.", {
            "analysis": self.state.previous_error_analysis
        })
        return result.json_dict

    # -----------------------------
    # 6) Interpret Results
    # -----------------------------
    @listen("interpret_result")
    async def generate_sql_interpretation(self):
        crew = SQLResultInterpreterCrew()
        date_now = self._get_current_datetime()

        result = await crew.crew().kickoff_async(
            inputs={
                "user_prompt": self.state.user_prompt or "",
                "sql_query": self.state.sql_query or "N/A",
                "sql_results": self.state.query_results[:40] or [],
                "date": date_now or "",
                "column_description": self.state.column_description or "",
            }
        )

        output = result.json_dict or {}
        if not output:
            return output

        output.setdefault("data", {})
        output["data"].update({"rows": self.state.query_results})

        self._trace("interpret_result", "Generated business interpretation.", {
            "has_summary": bool(output.get("summary")),
            "rows_returned": len(self.state.query_results),
        })

        # Attach trace for frontend
        output["trace"] = getattr(self.state, "execution_trace", [])
        return output

    # -----------------------------
    # 7) Max retries exceeded
    # -----------------------------
    @listen("max_retries_exceeded")
    def handle_max_retries(self):
        self._trace("max_retries_exceeded", "Retries exceeded.")
        return {
            "summary": "Maximum retry attempts exceeded. Please modify your prompt and try again.",
            "trace": getattr(self.state, "execution_trace", []),
        }
