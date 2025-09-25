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
    previous_error: str | None = Field(
        default=None,
        description="The error message from the SQL execution attempt, if any.",
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
