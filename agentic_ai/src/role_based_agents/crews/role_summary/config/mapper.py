# mapper.py

# --- Agent Definitions ---
AGENTS = {
    "status_summary_agent": {
        "role": "Status Analyzer",
        "goal": "Provide a clear breakdown of milestone statuses for the selected role.",
        "backstory": (
            "A specialist agent that reviews all milestones associated with the role "
            "and identifies their current status distribution (Complete, Delayed, "
            "Pending, In Progress). Helps detect bottlenecks and track execution health."
        ),
    },
    "delay_analysis_agent": {
        "role": "Cycle Time Benchmarking Agent",
        "goal": "Identify delays by comparing planned vs actual durations.",
        "backstory": (
            "A benchmarking agent responsible for calculating cycle slippages and "
            "highlighting projects where planned dates significantly diverge from "
            "actual completion."
        ),
    },
    "anomaly_triage_agent": {
        "role": "Anomaly Detector",
        "goal": "Detect, classify, and explain anomalies tied to the role.",
        "backstory": (
            "A triage-focused agent that identifies systemic anomalies such as missing "
            "dates, extremely long durations, or vendor-caused delays, with attention "
            "to severity levels."
        ),
    },
    "vendor_attribution_agent": {
        "role": "Vendor Attribution Specialist",
        "goal": "Attribute delays to vendors and explain vendor accountability.",
        "backstory": (
            "A vendor-performance analyst that correlates milestone delays with vendor "
            "participation, highlighting vendors most frequently associated with slippages."
        ),
    },
    "dependency_mapping_agent": {
        "role": "Dependency Mapper",
        "goal": "Show the role’s dependency flow and its bottlenecks.",
        "backstory": (
            "A workflow mapper agent that illustrates how dependencies propagate delays, "
            "mapping prerequisite and successor milestones to explain cascading impacts."
        ),
    },
    "meta_summary_agent": {
        "role": "Meta Summarizer",
        "goal": "Assemble role-specific insights into one cohesive executive narrative.",
        "backstory": (
            "A senior orchestration agent that collects insights from status, delays, "
            "anomalies, vendor impacts, and dependency flows, and produces a unified "
            "summary with risks and next actions."
        ),
    },
}

# --- Task Definitions ---
TASKS = {
    "status_summary_task": {
        "description": "Summarize milestone statuses for the selected role.",
        "expected_output": {
            "summary": "Plain language interpretation of status distribution",
            "status_counts": {...},
        },
        "agent": "status_summary_agent",
    },
    "delay_analysis_task": {
        "description": (
            "Compare planned vs actual milestone durations, compute delays, "
            "and highlight projects most at risk."
        ),
        "expected_output": {
            "summary": "Interpretation of delays across projects",
            "delays": [...],
        },
        "agent": "delay_analysis_agent",
    },
    "anomaly_triage_task": {
        "description": (
            "Detect and classify anomalies tied to the selected role. Summarize "
            "frequency, severity, and provide explanations for anomalies."
        ),
        "expected_output": {
            "summary": "Interpretation of anomalies",
            "anomalies": [...],
        },
        "agent": "anomaly_triage_agent",
    },
    "vendor_attribution_task": {
        "description": (
            "Attribute milestone delays to vendors, explaining which vendors are linked "
            "to slippages and where accountability lies."
        ),
        "expected_output": {
            "summary": "Interpretation of vendor impact",
            "impacts": [...],
        },
        "agent": "vendor_attribution_agent",
    },
    "dependency_task": {
        "description": (
            "Map role dependencies across workflow and explain bottlenecks caused by "
            "upstream or downstream milestones."
        ),
        "expected_output": {
            "summary": "Dependency flow explanation",
            "dependencies": [...],
        },
        "agent": "dependency_mapping_agent",
    },
    "final_composition_task": {
        "description": (
            "Assemble all role-specific outputs into one cohesive executive narrative "
            "including headline, top risks, and recommended next actions."
        ),
        "expected_output": {
            "headline": "...",
            "risks": [...],
            "next_actions": [...],
        },
        "agent": "meta_summary_agent",
    },
}


def get_agent_details(agent_key: str):
    """Return agent details dict from hard-coded mapping."""
    return AGENTS.get(agent_key, {})


def get_task_details(task_key: str):
    """Return task details dict from hard-coded mapping."""
    return TASKS.get(task_key, {})
