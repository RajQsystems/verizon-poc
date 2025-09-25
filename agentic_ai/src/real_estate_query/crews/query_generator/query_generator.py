from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class SQLResultInterpreterCrew:
    """A Crew that interprets SQL query results and provides insights."""

    agents: list[BaseAgent]
    tasks: list[Task]

    _llm = LLM(model="gpt-4.1", temperature=0.25)

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def query_planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["query_planner_agent"],  # type: ignore[index]
            llm=self._llm,
        )

    @agent
    def query_generator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["query_generator_agent"],  # type: ignore[index]
            llm=self._llm,
        )

    @task
    def query_planner_task(self) -> Task:
        return Task(
            config=self.tasks_config["query_planner_task"],  # type: ignore[index]
        )

    @task
    def query_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config["query_generation_task"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
