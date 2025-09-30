from typing import Any, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, validator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from backend.app.db.session import AsyncSessionLocal


class SQLQueryToolInput(BaseModel):
    """Input schema for the SQLQueryTool."""

    table: str = Field(..., description="The exact database table name to query.")
    column: str = Field(
        ..., description="The exact column name from which to retrieve distinct values."
    )

    @validator("table", "column")
    def validate_identifiers(cls, v: str) -> str:
        # Only allow safe alphanumeric + underscore identifiers
        if not v.replace("_", "").isalnum():
            raise ValueError(f"Invalid identifier: {v}")
        return v


class SQLQueryTool(BaseTool):
    name: str = "SQLQueryTool"
    description: str = (
        "Use this tool to fetch the DISTINCT values of a specific column "
        "from a specific table in the Verizon schema. "
        "Useful for resolving IN queries, checking categorical values, "
        "and validating column contents."
    )
    args_schema: Type[BaseModel] = SQLQueryToolInput

    async def _run(self, **kwargs: Any):
        table = kwargs.get("table")
        column = kwargs.get("column")

        try:
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    stmt = text(f"""
                        SELECT DISTINCT {column}
                        FROM {table}
                        WHERE {column} IS NOT NULL
                    """)
                    result = await session.execute(stmt)
                    distinct_values = [row[0] for row in result.fetchall()]

            return {
                "table": table,
                "column": column,
                "distinct_values": distinct_values,
                "count": len(distinct_values),
            }

        except SQLAlchemyError as e:
            return {"error": f"SQLAlchemy error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
