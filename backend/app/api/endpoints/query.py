from fastapi import APIRouter

from backend.app.schemas import QueryRequest
from agentic_ai import sql_query_generator

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("")
async def post_query(query: QueryRequest):
    result = await sql_query_generator(user_prompt=query.user_query)
    return result
