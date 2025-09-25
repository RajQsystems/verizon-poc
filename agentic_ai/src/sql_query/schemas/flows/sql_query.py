from typing import Any
from pydantic import BaseModel, Field


class SQLQueryState(BaseModel):
    user_prompt: str = Field(
        default="",
        description="The user's prompt that needs to be converted into an SQL query.",
    )
    logical_query_plan: str = Field(
        default="",
        description="The intermediate query plan generated from the user prompt.",
    )
    previous_error: list[str | None] = Field(
        default_factory=list,
        description="The error message from the SQL execution attempt, if any.",
    )
    previous_error_analysis: dict = Field(
        default={},
        description="The analysis of the previous SQL error.",
    )
    query_results: Any = Field(
        default_factory=list,
        description="The results obtained from executing the SQL query.",
    )
    column_description: str = Field(
        default="",
        description="Description of the database table columns.",
    )
    retry_count: int = Field(
        default=0,
        description="The number of times the SQL query generation has been retried.",
    )
    has_sql_error: bool = Field(
        default=False,
        description="Indicates whether the last SQL execution resulted in an error.",
    )
