from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    user_query: str = Field(
        default="", description="The user's query in natural language."
    )
