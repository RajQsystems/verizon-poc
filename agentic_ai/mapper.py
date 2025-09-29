# --- Agent Definitions ---
AGENTS = {
    "project_overview_agent": {
        "role": "Project Overview Synthesizer",
        "goal": "Consume the /projects/{project_id}/summary payload and generate a clear, normalized overview...",
        "backstory": "You are the first-pass analyst... stable internal shape (overview_json)...",
    },
    "milestone_diagnostic_agent": {
        "role": "Milestone Diagnostic Specialist",
        "goal": "Separate healthy vs delayed milestones, identify patterns...",
        "backstory": "You read milestone timelines like ECGs...",
    },
    "anomaly_triage_agent": {
        "role": "Anomaly Triage & Severity Assessor",
        "goal": "Classify anomalies by type and severity...",
        "backstory": "You're the on-call incident commander...",
    },
    "cycle_benchmark_agent": {
        "role": "Cycle-Time Benchmark Analyst",
        "goal": "Benchmark planned vs actual durations per cycle...",
        "backstory": "You're obsessed with time-to-market...",
    },
    "zoning_focus_agent": {
        "role": "Zoning Critical-Path Examiner",
        "goal": "Perform a zoning-first analysis...",
        "backstory": "You know zoning delays ripple everywhere...",
    },
    "vendor_attribution_agent": {
        "role": "Vendor Attribution & Accountability",
        "goal": "Attribute delays to vendors where possible...",
        "backstory": "Contracts meet reality here...",
    },
    "meta_summary_agent": {
        "role": "Executive-Level Composer",
        "goal": "Merge outputs into a concise narrative with prioritized actions...",
        "backstory": "You write for busy leaders...",
    },
}

# --- Task Definitions ---
TASKS = {
    "fetch_project_summary_task": {
        "description": "Call backend /projects/{project_id}/summary...",
        "steps": [
            "Invoke GET /projects/{project_id}/summary",
            "Validate presence of project, milestones, anomalies, cycles",
            "Return raw JSON as overview",
        ],
        "expected_output": "{ overview: {...}, notes: [] }",
        "agent": "project_overview_agent",
        "previous": None,
        "next": ["milestone_analysis_task", "anomaly_triage_task", "cycle_benchmark_task"],
    },
    "milestone_analysis_task": {
        "description": "Transform milestones into analytics-ready signals...",
        "steps": ["Separate healthy vs delayed", "Group delayed", "Top 5 delayed", "Flag weird cases"],
        "expected_output": "{ summary: {...}, delayed_by_agent: [...], ... }",
        "agent": "milestone_diagnostic_agent",
        "previous": ["fetch_project_summary_task"],
        "next": ["zoning_focus_task", "vendor_attribution_task"],
    },
    "anomaly_triage_task": {
        "description": "Build a risk register from overview.anomalies.details...",
        "steps": ["Group by severity", "Pull top examples", "Compute risk_score"],
        "expected_output": "{ counts_by_severity: {...}, top_risks: [...] }",
        "agent": "anomaly_triage_agent",
        "previous": ["fetch_project_summary_task"],
        "next": ["zoning_focus_task", "final_composition_task"],
    },
    "cycle_benchmark_task": {
        "description": "Analyze cycles array, compute SLA breaches...",
        "steps": ["Lookup SLA", "Compute variance", "Mark breaches"],
        "expected_output": "{ cycles: [...], breaches: N }",
        "agent": "cycle_benchmark_agent",
        "previous": ["fetch_project_summary_task"],
        "next": ["final_composition_task"],
    },
    "zoning_focus_task": {
        "description": "Perform zoning-first review...",
        "steps": ["Scan delayed milestones", "Scan anomalies", "Link leasing blockers", "Action plan"],
        "expected_output": "{ zoning_findings: [...], upstream_links: [...], action_plan: [...] }",
        "agent": "zoning_focus_agent",
        "previous": ["fetch_project_summary_task", "milestone_analysis_task", "anomaly_triage_task"],
        "next": ["final_composition_task"],
    },
    "vendor_attribution_task": {
        "description": "Attribute delays to vendors where possible...",
        "steps": ["Map milestones to vendor domain", "Count delayed", "Draft asks"],
        "expected_output": "{ by_vendor_domain: [...], asks: [...] }",
        "agent": "vendor_attribution_agent",
        "previous": ["fetch_project_summary_task", "milestone_analysis_task"],
        "next": ["final_composition_task"],
    },
    "final_composition_task": {
        "description": "Integrate all signals into executive summary...",
        "steps": ["Synthesize risks", "Synthesize actions", "Be concise"],
        "expected_output": "{ headline: ..., top_risks: [...], next_actions: [...] }",
        "agent": "meta_summary_agent",
        "previous": [
            "milestone_analysis_task",
            "anomaly_triage_task",
            "cycle_benchmark_task",
            "zoning_focus_task",
            "vendor_attribution_task",
        ],
        "next": None,
    },
}

# --- Explicit Mapping (redundant but useful) ---
TASK_TO_AGENT = {task: details["agent"] for task, details in TASKS.items()}
