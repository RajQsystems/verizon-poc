# result_interpreter.py
from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from agentic_ai.src.sql_query.schemas import ResultInterpretationTaskOutput


@CrewBase
class SQLResultInterpreterCrew:
    """Crew for interpreting SQL query results into business insights."""

    agents: list[BaseAgent]
    tasks: list[Task]

    _llm = LLM(model="gpt-4.1", temperature=0.2, reasoning_effort="medium")

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ----------------------
    # Agents
    # ----------------------
    @agent
    def result_analysis_agent(self) -> Agent:
        """Agent that analyzes raw SQL results and generates business insights."""
        return Agent(
            config=self.agents_config["result_analysis_agent"],  # type: ignore[index]
            llm=self._llm,
        )

    # ----------------------
    # Tasks
    # ----------------------
    @task
    def interpret_sql_results_task(self) -> Task:
        """Task that transforms SQL query outputs into actionable narratives."""
        return Task(
            config=self.tasks_config["interpret_sql_results_task"],  # type: ignore[index]
            output_json=ResultInterpretationTaskOutput,
        )

    # ----------------------
    # Crew definition
    # ----------------------
    @crew
    def crew(self) -> Crew:
        """Sequential crew: run analysis task with result_analysis_agent."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
