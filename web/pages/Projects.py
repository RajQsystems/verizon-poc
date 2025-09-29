import requests
import streamlit as st
import graphviz
import sys
import os

# Add project root (where agentic_ai/ lives) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agentic_ai.mapper import TASKS, AGENTS, TASK_TO_AGENT

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Agentic Project Summary", page_icon="📊", layout="wide")
st.title("📊 Agentic Project Summary — Live Run Viewer")

# --- Sidebar ---
st.sidebar.header("Run a Summary")
project_id = st.sidebar.text_input("Project ID", value="ID_277EA56BE3")
run_btn = st.sidebar.button("Run")

# --- Layout placeholders ---
status_box = st.empty()
left, right = st.columns([2, 1])

# --- Helpers ---
def call_json(url: str):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return r.json()

def render_overview(overview: dict):
    with st.expander("Overview (from /projects/{id}/summary)", expanded=True):
        proj = overview.get("project", {})
        st.subheader("Project")
        st.json(proj)

        ms = overview.get("milestones", {})
        st.subheader("Milestones")
        st.write(f"Total: **{ms.get('total')}**, Delayed: **{ms.get('delayed')}**")
        with st.expander("Healthy Milestones"):
            st.json(ms.get("healthy_milestones", []))
        with st.expander("Delayed Milestones"):
            st.json(ms.get("delayed_milestones", []))

        st.subheader("Anomalies")
        an = overview.get("anomalies", {})
        st.write(f"Count: **{an.get('count', 0)}**")
        with st.expander("Details"):
            st.json(an.get("details", []))

        st.subheader("Cycles")
        st.json(overview.get("cycles", []))

def render_trace(trace: list[dict]):
    st.subheader("Execution Trace")
    if not trace:
        st.write("— No trace recorded —")
    for evt in trace:
        with st.expander(
            f"[{evt.get('time','')}] {evt.get('step','')} — {evt.get('message','')}",
            expanded=False,
        ):
            st.json(evt.get("payload", {}))

def render_summary(headline: str, risks: list, actions: list, raw_output: str):
    st.subheader("Executive Summary")
    st.markdown(f"**Headline:** {headline or '—'}")

    st.markdown("**Top Risks:**")
    if risks:
        for r in risks:
            st.markdown(f"- {r}")
    else:
        st.write("—")

    st.markdown("**Next Actions:**")
    if actions:
        for a in actions:
            st.markdown(f"- {a}")
    else:
        st.write("—")

    with st.expander("Raw Output"):
        st.text(raw_output or "")

def render_agent_runs(runs: list[dict]):
    st.subheader("Agent Runs (per task)")
    if not runs:
        st.write("— No agent/task outputs recorded —")
        return
    for i, run in enumerate(runs, 1):
        title = run.get("display_name") or f"{run.get('agent_key','agent')} — {run.get('task_key','task')}"
        with st.expander(f"{i}. {title}", expanded=False):
            if run.get("output_json"):
                st.markdown("**JSON Output**")
                st.json(run["output_json"])
            if run.get("output_raw"):
                st.markdown("**Raw Output**")
                st.text(run["output_raw"])

def render_agents_debug(agents: list):
    st.subheader("🔍 Agent & Task Breakdown")
    for run in agents:
        # API returns dict, so use .get()
        display_name = run.get("display_name", f"{run.get('agent_key')} — {run.get('task_key')}")
        with st.expander(display_name):
            st.markdown("**Task Details**")
            st.json(run.get("task_details", {}))

            st.markdown("**Agent Details**")
            st.json(run.get("agent_details", {}))

            st.markdown("**Output**")
            if run.get("output_json"):
                st.json(run["output_json"])
            elif run.get("output_raw"):
                st.text(run["output_raw"])

def render_flowchart(agents: list):
    st.subheader("🕸️ Smart Agent–Task Flow")

    dot = graphviz.Digraph(format="svg")
    dot.attr(rankdir="LR", size="10")

    # --- Nodes ---
    for task_key, details in TASKS.items():
        agent_key = str(details.get("agent", ""))  # ✅ force string
        agent = AGENTS.get(agent_key, {})          # ✅ now safe

        # Task node (box)
        dot.node(
            task_key,
            label=f"{task_key}\n{details.get('description','')[:40]}...",
            shape="box",
            style="filled",
            color="lightblue",
            tooltip=details.get("description","")
        )

        # Agent node (ellipse)
        if agent_key and agent:
            dot.node(
                agent_key,
                label=f"{agent_key}\n({agent.get('role','')})",
                shape="ellipse",
                style="filled",
                color="lightgreen",
                tooltip=agent.get("goal","")
            )
            # Link agent → task
            dot.edge(agent_key, task_key, color="gray", style="dashed")

    # --- Edges (workflow order) ---
    for task_key, details in TASKS.items():
        for nxt in details.get("next", []) or []:
            dot.edge(task_key, nxt, color="black")

    st.graphviz_chart(dot, use_container_width=True)



# --- Main Run Flow ---
if run_btn:
    with st.status("Starting run…", expanded=True) as status:
        # Step 1: Fetch overview
        st.write("Step 1/2 — Fetching overview…")
        try:
            overview_url = f"{API_BASE}/projects/{project_id}/summary"
            overview = call_json(overview_url)
            status.update(label="Overview fetched.", state="running")
        except Exception as e:
            status.update(label="Failed fetching overview.", state="error")
            st.error(f"Error getting overview: {e}")
            st.stop()

        # Show overview immediately in left column
        with left:
            render_overview(overview)

        # Step 2: Run agentic pipeline
        st.write("Step 2/2 — Running agentic pipeline (crew)…")
        try:
            common_url = f"{API_BASE}/common/summary/{project_id}"
            result = call_json(common_url)
            status.update(label="Agentic pipeline complete.", state="complete")
        except Exception as e:
            status.update(label="Pipeline failed.", state="error")
            st.error(f"Error running pipeline: {e}")
            st.stop()

    # --- Right column: Final summary ---
    with right:
        render_summary(
            result.get("headline", ""),
            result.get("risks", []) or result.get("top_risks", []),
            result.get("actions", []) or result.get("next_actions", []),
            result.get("raw_output", ""),
        )

    # --- Below: trace and agent breakdown ---
    with st.container():
        render_trace(result.get("trace", []))
        render_agents_debug(result.get("agents", []))   # 👈 Now detailed
        render_flowchart(result.get("agents", []))   # 👈 NEW


