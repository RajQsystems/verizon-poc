from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from agentic_ai.src.sql_query.tools import SQLQueryTool


@CrewBase
class SQLQueryGeneratorCrew:
    """Crew for generating SQL queries from natural language prompts."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    _llm = LLM(model="gpt-4.1", temperature=0.15, reasoning_effort="low")

    @agent
    def query_interpretation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["query_interpretation_agent"],  # type: ignore[index]
            llm=self._llm,
        )

    @agent
    def query_generation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["query_generation_agent"],  # type: ignore[index]
            llm=self._llm,
        )

    @task
    def query_interpretation_task(self) -> Task:
        return Task(
            config=self.tasks_config["query_interpretation_task"],  # type: ignore[index]
        )

    @task
    def query_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config["query_generation_task"],  # type: ignore[index]
            tools=[SQLQueryTool()],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
