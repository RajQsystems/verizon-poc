from pydantic import BaseModel, Field


class DataColumns(BaseModel):
    columns: list[str] = Field(
        default_factory=list,
        description="List of column names",
    )


class ResultInterpretationTaskOutput(BaseModel):
    summary: str = Field(
        default="",
        description="A concise summary in Markdown format",
    )
    data: DataColumns = Field(..., description="Structured data with columns and rows")
    recommendations: list[str] = Field(
        default_factory=list,
        description="Actionable recommendations based on the SQL query results",
    )
    visualization_hints: dict[str, bool] = Field(
        default_factory=dict,
        description="Hints for visualizing the data, e.g., {'bar_chart': True, 'line_chart': False}",
    )
