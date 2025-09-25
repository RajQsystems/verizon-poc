from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.app.db.session import AsyncSessionLocal


class SQLQueryToolInput(BaseModel):
    """Input schema for the SQLQueryTool."""

    table: str = Field(..., description="The name of the database table to query.")
    column: str = Field(
        ..., description="The column from which to retrieve distinct values."
    )


class SQLQueryTool(BaseTool):
    name: str = "Name of my tool"
    description: str = "Clear description for what this tool is useful for, your agent will need this information to use it."
    args_schema: Type[BaseModel] = SQLQueryToolInput

    async def _run(self, **kwargs: Any):
        table = kwargs.get("table")
        column = kwargs.get("column")
        try:
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    result = await session.execute(
                        text(f"""
                            SELECT DISTINCT {column} 
                            FROM {table}
                            WHERE {column} IS NOT NULL
                       """)
                    )
                    distinct_values = [row[0] for row in result.fetchall()]
                    return distinct_values
        except SQLAlchemyError as e:
            return f"SQLAlchemy error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
