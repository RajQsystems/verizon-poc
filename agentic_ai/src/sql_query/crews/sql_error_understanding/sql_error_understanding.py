from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from agentic_ai.src.sql_query.schemas import SQLErrorUnderstandingOutput


@CrewBase
class SQLErrorUnderstandingCrew:
    """A Crew that interprets SQL query results and provides insights."""

    agents: list[BaseAgent]
    tasks: list[Task]

    _llm = LLM(model="gpt-4.1", temperature=0.25, reasoning_effort="medium")

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def error_understanding_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["error_understanding_agent"],  # type: ignore[index]
        )

    @task
    def error_understanding_task(self) -> Task:
        return Task(
            config=self.tasks_config["error_understanding_task"],  # type: ignore[index]
            output_json=SQLErrorUnderstandingOutput,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
