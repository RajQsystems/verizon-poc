# sql_error_understanding.py
from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from agentic_ai.src.sql_query.schemas import SQLErrorUnderstandingOutput


@CrewBase
class SQLErrorUnderstandingCrew:
    """Crew for analyzing and recovering from SQL execution errors."""

    agents: list[BaseAgent]
    tasks: list[Task]

    _llm = LLM(model="gpt-4.1", temperature=0.25, reasoning_effort="medium")

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ----------------------
    # Agents
    # ----------------------
    @agent
    def sql_error_analysis_agent(self) -> Agent:
        """Agent that diagnoses and classifies SQL errors."""
        return Agent(
            config=self.agents_config["sql_error_analysis_agent"],  # type: ignore[index]
            llm=self._llm,
        )

    @agent
    def sql_error_recovery_agent(self) -> Agent:
        """Agent that proposes fixes for SQL errors."""
        return Agent(
            config=self.agents_config["sql_error_recovery_agent"],  # type: ignore[index]
            llm=self._llm,
        )

    # ----------------------
    # Tasks
    # ----------------------
    @task
    def sql_error_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["sql_error_analysis_task"],  # type: ignore[index]
            output_json=SQLErrorUnderstandingOutput,
        )

    @task
    def sql_error_recovery_task(self) -> Task:
        return Task(
            config=self.tasks_config["sql_error_recovery_task"],  # type: ignore[index]
            output_json=SQLErrorUnderstandingOutput,
        )

    # ----------------------
    # Crew definition
    # ----------------------
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
