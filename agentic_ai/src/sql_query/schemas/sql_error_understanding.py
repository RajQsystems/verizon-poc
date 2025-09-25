from pydantic import BaseModel, Field


class SQLErrorUnderstandingOutput(BaseModel):
    error_type: str = Field(
        default="",
        description="The exact reason of the error as specified in SQLAlchemy error message and stack trace.",
    )
    affected_columns: list[str] = Field(
        default_factory=list,
        description="List of columns that caused the error.",
    )
    affected_tables: list[str] = Field(
        default_factory=list,
        description="List of table names if applicable, else [].",
    )
    suggested_corrections: list[dict[str, str]] = Field(
        default_factory=list,
        description=(
            "List of suggested corrections that the Query Planner can directly apply. "
            "Each correction is a dictionary with keys like 'action', 'from', and 'to'."
        ),
    )
