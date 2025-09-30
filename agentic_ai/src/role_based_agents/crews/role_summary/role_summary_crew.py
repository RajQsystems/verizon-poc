# backend/app/crews/role_summary_crew.py

from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class RoleSummaryCrew:
    """Role-Centric Summary Crew (Agent Performance Overview)"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # Point to the YAML configs you defined earlier
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Debugging loaders
        print("DEBUG RoleSummaryCrew → agents.yaml:", type(self.agents_config))
        print("DEBUG RoleSummaryCrew → tasks.yaml:", type(self.tasks_config))

        if isinstance(self.agents_config, dict):
            print("✅ Loaded agents:", self.agents_config.keys())
        else:
            print("❌ Could not load agents.yaml")

        if isinstance(self.tasks_config, dict):
            print("✅ Loaded tasks:", self.tasks_config.keys())
        else:
            print("❌ Could not load tasks.yaml")

    # ------------------ LLMs ------------------
    _status_llm = LLM(model="gpt-4.1", temperature=0.0)
    _delay_llm = LLM(model="gpt-4.1", temperature=0.1)
    _anomaly_llm = LLM(model="gpt-4.1", temperature=0.0)
    _vendor_llm = LLM(model="gpt-4.1", temperature=0.0)
    _dependency_llm = LLM(model="gpt-4.1", temperature=0.0)
    _meta_llm = LLM(model="gpt-4.1", temperature=0.2)

    # ------------------ AGENTS ------------------

    @agent
    def status_summary_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["status_summary_agent"],  # type: ignore[index]
            llm=self._status_llm,
        )

    @agent
    def delay_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["delay_analysis_agent"],  # type: ignore[index]
            llm=self._delay_llm,
        )

    @agent
    def anomaly_triage_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["anomaly_triage_agent"],  # type: ignore[index]
            llm=self._anomaly_llm,
        )

    @agent
    def vendor_attribution_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["vendor_attribution_agent"],  # type: ignore[index]
            llm=self._vendor_llm,
        )

    @agent
    def dependency_mapping_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["dependency_mapping_agent"],  # type: ignore[index]
            llm=self._dependency_llm,
        )

    @agent
    def meta_summary_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["meta_summary_agent"],  # type: ignore[index]
            llm=self._meta_llm,
        )

    # ------------------ TASKS ------------------

    @task
    def status_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config["status_summary_task"],  # type: ignore[index]
        )

    @task
    def delay_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["delay_analysis_task"],  # type: ignore[index]
        )

    @task
    def anomaly_triage_task(self) -> Task:
        return Task(
            config=self.tasks_config["anomaly_triage_task"],  # type: ignore[index]
        )

    @task
    def vendor_attribution_task(self) -> Task:
        return Task(
            config=self.tasks_config["vendor_attribution_task"],  # type: ignore[index]
        )

    @task
    def dependency_task(self) -> Task:
        return Task(
            config=self.tasks_config["dependency_task"],  # type: ignore[index]
        )

    @task
    def final_composition_task(self) -> Task:
        return Task(
            config=self.tasks_config["final_composition_task"],  # type: ignore[index]
        )

    # ------------------ CREW ------------------

    @crew
    def crew(self) -> Crew:
        """Defines the full pipeline for Role Summary"""
        return Crew(
            agents=self.agents,
            tasks=[
                self.status_summary_task(),
                self.delay_analysis_task(),
                self.anomaly_triage_task(),
                self.vendor_attribution_task(),
                self.dependency_task(),
                self.final_composition_task(),
            ],
            process=Process.sequential,  # Run in strict order
            verbose=True,
        )
