from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class ConstructionQueryGeneratorCrew:
    """Crew for generating construction-focused SQL queries from natural language prompts."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    _llm = LLM(model="gpt-4.1", temperature=0.15, reasoning_effort="low")

    @agent
    def construction_query_interpretation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["construction_query_interpretation_agent"],  # type: ignore[index]
            llm=self._llm,
        )

    @agent
    def construction_query_generation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["construction_query_generation_agent"],  # type: ignore[index]
            llm=self._llm,
        )

    @task
    def construction_query_interpretation_task(self) -> Task:
        return Task(
            config=self.tasks_config["construction_query_interpretation_task"],  # type: ignore[index]
        )

    @task
    def construction_query_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config["construction_query_generation_task"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
