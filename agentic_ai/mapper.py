# --- Agent Definitions ---
AGENTS = {
    "project_overview_agent": {
        "role": "Project Overview Synthesizer",
        "goal": (
            "Consume the projects/{project_id}/summary payload and generate a clear, normalized overview that other agents can rely on. "
            "Extract essentials: project meta, milestone groupings, anomaly inventory, and cycle metrics."
        ),
        "backstory": (
            "You are the first-pass analyst. You don't guess—you structure. You turn heterogeneous API output into a stable internal shape (overview_json) with normalized keys, "
            "so downstream agents never have to parse raw responses."
        ),
        "verbose": True,
    },
    "milestone_diagnostic_agent": {
        "role": "Milestone Diagnostic Specialist",
        "goal": (
            "Separate healthy vs delayed milestones, identify patterns by agent and name, "
            "and call out likely root causes using dependency hints and status deltas."
        ),
        "backstory": (
            "You read milestone timelines like ECGs. You highlight where the rhythm breaks—prolonged Delayed, missing actual dates, negative durations, and clustering by agent (Zoning, Construction, Transport, etc.)."
        ),
        "verbose": True,
    },
    "anomaly_triage_agent": {
        "role": "Anomaly Triage & Severity Assessor",
        "goal": (
            "Classify anomalies by type and severity, prioritize critical ones (e.g. Zoning Missing Date, Long Duration 500d, Transport Vendor Delay), "
            "and summarize impact on project delivery."
        ),
        "backstory": (
            "You're the on-call incident commander for delivery risks. You triage, cluster, and translate anomaly lists into an actionable risk register."
        ),
        "verbose": True,
    },
    "cycle_benchmark_agent": {
        "role": "Cycle-Time Benchmark Analyst",
        "goal": (
            "Benchmark planned vs actual durations per cycle (StartRER, RECRTC, Transport ContractDelivery). "
            "Compute variances, detect SLA breaches, and compare against rolling medians if available."
        ),
        "backstory": (
            "You're obsessed with time-to-market. Variance is your native language. You flag any drift that matters to deployment velocity."
        ),
        "verbose": True,
    },
    "zoning_focus_agent": {
        "role": "Zoning Critical-Path Examiner",
        "goal": (
            "Perform a zoning-first analysis. If Zoning is present, identify blockers, missing dates, dependency waits (e.g. Leasing), "
            "and expected clearance timeline given historical patterns."
        ),
        "backstory": (
            "You know that zoning delays ripple everywhere. Your job is to extract zoning-specific insights and put them front and center."
        ),
        "verbose": True,
    },
    "vendor_attribution_agent": {
        "role": "Vendor Attribution & Accountability",
        "goal": (
            "Attribute delays to vendors where possible, especially Transport Delivery and Construction. "
            "Produce a per-vendor risk lens and next-step asks."
        ),
        "backstory": (
            "Contracts meet reality here. You gather vendor-linked delays and quantify their impact with crisp recommendations."
        ),
        "verbose": True,
    },
    "meta_summary_agent": {
        "role": "Executive-Level Composer",
        "goal": (
            "Merge outputs from diagnostics, anomaly triage, cycles, zoning focus, and vendor attribution into a single concise narrative with prioritized actions."
        ),
        "backstory": (
            "You write for busy leaders: crisp headline, top 3 risks, next 3 actions, and a simple ETA outlook with confidence."
        ),
        "verbose": True,
    },
}

# --- Task Definitions ---
TASKS = {
    "fetch_project_summary_task": {
        "description": (
            "Call the backend projects/{project_id}/summary endpoint and return the structured payload as overview. Do not mutate fields. "
            "If any top-level key is missing, include a notes key to highlight gaps."
        ),
        "steps": [
            "Invoke GET /projects/{project_id}/summary",
            "Validate presence of project, milestones, anomalies, cycles",
            "Return the raw JSON as overview plus a notes list for any gaps"
        ],
        "expected_output": "{ overview: {...}, notes: [] }",
        "agent": "project_overview_agent",
        "previous": None,
        "next": [
            "milestone_analysis_task",
            "anomaly_triage_task",
            "cycle_benchmark_task"
        ],
    },
    "milestone_analysis_task": {
        "description": (
            "Transform the milestones section into analytics-ready signals: counts, delayed clusters by agent and milestone name, "
            "top 5 late items with days, and early hypotheses on root cause using dependency hints."
        ),
        "steps": [
            "Separate healthy vs delayed from overview.milestones",
            "Group delayed by agent_id and milestone name",
            "Select top 5 delayed by duration_days",
            "Flag weird cases (negative duration, missing actual_date for past planned_date)"
        ],
        "expected_output": "{ summary: {...}, delayed_by_agent: [...], top_late: [...], weird_cases: [...] }",
        "agent": "milestone_diagnostic_agent",
        "previous": ["fetch_project_summary_task"],
        "next": [
            "zoning_focus_task",
            "vendor_attribution_task"
        ],
    },
    "anomaly_triage_task": {
        "description": (
            "Build a risk register from overview.anomalies.details. Prioritize High, summarize by type, and produce a crisp so-what for leadership."
        ),
        "steps": [
            "Group by severity and type",
            "Pull top examples for High severity (e.g. Zoning Missing Date)",
            "Create a risk_score heuristic: High=3, Medium=2, Low=1",
            "Compute total risk_score and top_risks list"
        ],
        "expected_output": "{ counts_by_severity: {...}, counts_by_type: {...}, risk_score: N, top_risks: [...] }",
        "agent": "anomaly_triage_agent",
        "previous": ["fetch_project_summary_task"],
        "next": [
            "zoning_focus_task",
            "final_composition_task"
        ],
    },
    "cycle_benchmark_task": {
        "description": (
            "Analyze cycles array. For each cycle, compute breach variance (SLA_days), where SLA defaults to 20 unless per-label SLA is provided. "
            "Return a compact table plus highlights."
        ),
        "steps": [
            "For each cycle, lookup SLA or default 20",
            "Compute breach variance from SLA",
            "Return list of label, planned, actual, variance, SLA, breach"
        ],
        "expected_output": "{ cycles: [...], breaches: N }",
        "agent": "cycle_benchmark_agent",
        "previous": ["fetch_project_summary_task"],
        "next": ["final_composition_task"],
    },
    "zoning_focus_task": {
        "description": (
            "Perform a zoning-first review. If anomalies refer to Zoning or milestones named Zoning Submitted/Approved are delayed or missing actuals, "
            "capture blockers and recommend the next best action."
        ),
        "steps": [
            "Scan delayed milestones for names containing Zoning",
            "Scan anomalies for Zoning in description or type",
            "If leasing milestone delays exist, link as upstream blocker",
            "Produce action plan with concrete owners and timestamps"
        ],
        "expected_output": "{ zoning_findings: [...], upstream_links: [...], action_plan: [...] }",
        "agent": "zoning_focus_agent",
        "previous": [
            "fetch_project_summary_task",
            "milestone_analysis_task",
            "anomaly_triage_task"
        ],
        "next": [
            "final_composition_task"
        ],
    },
    "vendor_attribution_task": {
        "description": (
            "Attribute delays to vendors where possible, using milestone names and known mappings (Transport, Construction, Leasing). "
            "Output a vendor risk table ranked by delayed milestone count and narrative asks."
        ),
        "steps": [
            "Map milestone to vendor domain (Transport, Construction, Leasing)",
            "Count delayed milestones per vendor domain",
            "Draft asks for top offenders (e.g. delivery date, crew allocation)"
        ],
        "expected_output": "{ by_vendor_domain: [...], asks: [...] }",
        "agent": "vendor_attribution_agent",
        "previous": [
            "fetch_project_summary_task",
            "milestone_analysis_task"
        ],
        "next": [
            "final_composition_task"
        ],
    },
    "final_composition_task": {
        "description": (
            "Integrate milestone, anomaly, cycle, zoning, and vendor attribution into a single executive summary. "
            "Include a headline, top 3 risks, and next 3 actions."
        ),
        "steps": [
            "Synthesize signals into 3 bullets for risks and 3 for actions",
            "Reference concrete milestones and anomaly IDs where relevant",
            "Be concise and executive-friendly"
        ],
        "expected_output": "{ headline: ..., top_risks: [...], next_actions: [...] }",
        "agent": "meta_summary_agent",
        "previous": [
            "milestone_analysis_task",
            "anomaly_triage_task",
            "cycle_benchmark_task",
            "zoning_focus_task",
            "vendor_attribution_task"
        ],
        "next": None,
    },
}

# --- Explicit Mapping (redundant but useful) ---
TASK_TO_AGENT = {task: details["agent"] for task, details in TASKS.items()}
