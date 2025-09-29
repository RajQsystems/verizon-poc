from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class ProjectSummaryCrew:
    """Project Summary Analysis Crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # Match ConstructionErrorUnderstandingCrew
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("DEBUG agents_config type:", type(self.agents_config))
        print("DEBUG tasks_config type:", type(self.tasks_config))

        if isinstance(self.agents_config, dict):
            print("✅ agents.yaml loaded keys:", self.agents_config.keys())
        else:
            print("❌ agents.yaml not loaded")

        if isinstance(self.tasks_config, dict):
            print("✅ tasks.yaml loaded keys:", self.tasks_config.keys())
        else:
            print("❌ tasks.yaml not loaded")

    

    # ------------------ LLMs ------------------
    _overview_llm = LLM(model="gpt-4.1", temperature=0.0)
    _milestone_llm = LLM(model="gpt-4.1", temperature=0.1)
    _anomaly_llm = LLM(model="gpt-4.1", temperature=0.0)
    _cycle_llm = LLM(model="gpt-4.1", temperature=0.0)
    _zoning_llm = LLM(model="gpt-4.1", temperature=0.0)
    _vendor_llm = LLM(model="gpt-4.1", temperature=0.0)
    _meta_llm = LLM(model="gpt-4.1", temperature=0.2)

    # ------------------ AGENTS ------------------

    @agent
    def project_overview_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["project_overview_agent"],  # type: ignore[index]
            llm=self._overview_llm,
        )

    @agent
    def milestone_diagnostic_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["milestone_diagnostic_agent"],  # type: ignore[index]
            llm=self._milestone_llm,
        )

    @agent
    def anomaly_triage_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["anomaly_triage_agent"],  # type: ignore[index]
            llm=self._anomaly_llm,
        )

    @agent
    def cycle_benchmark_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["cycle_benchmark_agent"],  # type: ignore[index]
            llm=self._cycle_llm,
        )

    @agent
    def zoning_focus_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["zoning_focus_agent"],  # type: ignore[index]
            llm=self._zoning_llm,
        )

    @agent
    def vendor_attribution_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["vendor_attribution_agent"],  # type: ignore[index]
            llm=self._vendor_llm,
        )

    @agent
    def meta_summary_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["meta_summary_agent"],  # type: ignore[index]
            llm=self._meta_llm,
        )

    # ------------------ TASKS ------------------

    @task
    def fetch_project_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_project_summary_task"],  # type: ignore[index]
        )

    @task
    def milestone_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["milestone_analysis_task"],  # type: ignore[index]
        )

    @task
    def anomaly_triage_task(self) -> Task:
        return Task(
            config=self.tasks_config["anomaly_triage_task"],  # type: ignore[index]
        )

    @task
    def cycle_benchmark_task(self) -> Task:
        return Task(
            config=self.tasks_config["cycle_benchmark_task"],  # type: ignore[index]
        )

    @task
    def zoning_focus_task(self) -> Task:
        return Task(
            config=self.tasks_config["zoning_focus_task"],  # type: ignore[index]
        )

    @task
    def vendor_attribution_task(self) -> Task:
        return Task(
            config=self.tasks_config["vendor_attribution_task"],  # type: ignore[index]
        )

    @task
    def final_composition_task(self) -> Task:
        return Task(
            config=self.tasks_config["final_composition_task"],  # type: ignore[index]
        )

    # ------------------ CREW ------------------

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=[
                self.fetch_project_summary_task(),
                self.milestone_analysis_task(),
                self.anomaly_triage_task(),
                self.cycle_benchmark_task(),
                self.zoning_focus_task(),
                self.vendor_attribution_task(),
                self.final_composition_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )
