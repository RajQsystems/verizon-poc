from agentic_ai.src.sql_query import SQLQueryGeneratorFlow
from agentic_ai.src.real_estate_query import RealEsateFlow
from agentic_ai.src.construction_query import ConstructionQueryFlow
from agentic_ai.exceptions import APIError


async def sql_query_generator(user_prompt: str) -> None:
    try:
        flow = SQLQueryGeneratorFlow()
        result = await flow.kickoff_async(inputs={"user_prompt": user_prompt})
        return result
    except APIError:
        raise


async def real_estate_query(user_prompt: str) -> None:
    try:
        flow = RealEsateFlow()
        flow.plot("real_estate_flow")
    except APIError:
        raise


async def construction_query_generator(user_prompt: str) -> None:
    try:
        flow = ConstructionQueryFlow()
        flow.plot("construction_query_flow")
    except APIError:
        raise
