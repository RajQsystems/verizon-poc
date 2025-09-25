from agentic_ai.src.sql_query import SQLQueryGeneratorFlow
from agentic_ai.exceptions import APIError


async def sql_query_generator(user_prompt: str) -> None:
    try:
        flow = SQLQueryGeneratorFlow()
        flow.plot("sql_query_flow")
        result = await flow.kickoff_async(inputs={"user_prompt": user_prompt})
        return result
    except APIError:
        raise
