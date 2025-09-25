from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from agentic_ai.src.sql_query.schemas import ResultInterpretationTaskOutput


@CrewBase
class SQLResultInterpreterCrew:
    """A Crew that interprets SQL query results and provides insights."""

    agents: list[BaseAgent]
    tasks: list[Task]

    _llm = LLM(model="gpt-4.1", temperature=0.4)

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def result_interpretation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["result_interpretation_agent"],  # type: ignore[index]
        )

    @task
    def result_interpretation_task(self) -> Task:
        return Task(
            config=self.tasks_config["result_interpretation_task"],  # type: ignore[index]
            output_json=ResultInterpretationTaskOutput,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
