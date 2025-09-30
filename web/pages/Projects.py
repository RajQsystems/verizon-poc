# web/pages/Projects.py
import requests
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agentic_ai.mapper import TASKS, AGENTS

API_BASE = "http://localhost:8000/api/v1"

# BASE_URL = os.getenv("BASE_URL")
# API_BASE = f"{BASE_URL}/api/v1"

st.set_page_config(page_title="Agentic Project Summary", page_icon="📊", layout="wide")
st.title("📊 Agentic Project Summary — Live Run Viewer")

# ------------------------
# Sidebar
# ------------------------
st.sidebar.header("Run a Summary")
project_id = st.sidebar.text_input("Project ID", value="ID_277EA56BE3")
run_btn = st.sidebar.button("Run")

# ------------------------
# Helpers
# ------------------------
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

# ------------------------
# Interactive Flow (PyVis)
# ------------------------
def render_interactive_flow():
    st.subheader("🕸️ Smart Agent–Task Flow")

    net = Network(
        height="800px", 
        width="100%", 
        directed=True,
        bgcolor="#222222"
    )
    net.force_atlas_2based(gravity=-50, central_gravity=0.02, spring_length=200, spring_strength=0.08)

    all_nodes = set()

    for task_key, details in TASKS.items():
        agent_key = details["agent"]

        if task_key not in all_nodes:
            net.add_node(task_key, label=task_key, color="lightblue", shape="box")
            all_nodes.add(task_key)

        if agent_key not in all_nodes:
            net.add_node(agent_key, label=agent_key, color="lightgreen", shape="ellipse")
            all_nodes.add(agent_key)

        net.add_edge(agent_key, task_key, color="gray", title="assigned")

        for nxt in details.get("next", []) or []:
            if nxt not in all_nodes:
                net.add_node(nxt, label=nxt, color="lightblue", shape="box")
                all_nodes.add(nxt)
            net.add_edge(task_key, nxt, color="white", title="next")

    net.save_graph("graph.html")
    with open("graph.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=800, scrolling=True)

    # Node selector (workaround for missing click → Streamlit event)
    # selected = st.selectbox("🔎 Select a node to expand details:", sorted(all_nodes))
    # if selected:
    #     st.session_state["selected_node"] = selected

# ------------------------
# Agent/Task details panel
# ------------------------
def render_agents_debug(agents_runs: list[dict]):
    st.subheader("🔍 Agent & Task Breakdown")
    for i, run in enumerate(agents_runs, 1):
        agent_key = run.get("agent_key") or ""
        task_key = run.get("task_key") or ""
        display = f"{agent_key} — {task_key}" if agent_key and task_key else f"Run {i}"

        with st.expander(f"{i}. {display}", expanded=False):
            mapper_task = TASKS.get(task_key, {})
            mapper_agent = AGENTS.get(agent_key, {})

            st.markdown("**Task Details**")
            st.json({
                "current_task": task_key,
                "description": mapper_task.get("description"),
                "steps": mapper_task.get("steps"),
                "expected_output": mapper_task.get("expected_output"),
                "previous": mapper_task.get("previous"),
                "next": mapper_task.get("next"),
                "associated_agent": mapper_task.get("agent"),
            })

            st.markdown("**Agent Details**")
            st.json({
                "agent_key": agent_key,
                "role": mapper_agent.get("role"),
                "goal": mapper_agent.get("goal"),
                "backstory": mapper_agent.get("backstory"),
            })

            st.markdown("**Captured Output**")
            if run.get("output_json"):
                st.json(run["output_json"])
            elif run.get("output_raw"):
                st.text(run["output_raw"])
            else:
                st.write("—")

# ------------------------
# Main
# ------------------------
if run_btn:
    with st.status("Starting run…", expanded=True) as status:
        # Step 1: Overview
        st.write("Step 1/2 — Fetching overview…")
        try:
            overview_url = f"{API_BASE}/projects/{project_id}/summary"
            overview = call_json(overview_url)
            st.session_state["overview"] = overview
            status.update(label="Overview fetched.", state="running")
        except Exception as e:
            status.update(label="Failed fetching overview.", state="error")
            st.error(f"Error getting overview: {e}")
            st.stop()

        # Step 2: Run pipeline
        st.write("Step 2/2 — Running agentic pipeline (crew)…")
        try:
            common_url = f"{API_BASE}/common/summary/{project_id}"
            result = call_json(common_url)
            st.session_state["result"] = result
            status.update(label="Agentic pipeline complete.", state="complete")
        except Exception as e:
            status.update(label="Pipeline failed.", state="error")
            st.error(f"Error running pipeline: {e}")
            st.stop()

# Render cached results
overview = st.session_state.get("overview")
result = st.session_state.get("result")

if overview and result:
    left, right = st.columns([2, 1])

    with left:
        render_overview(overview)

    with right:
        render_summary(
            result.get("headline", ""),
            result.get("risks", []) or result.get("top_risks", []),
            result.get("actions", []) or result.get("next_actions", []),
            result.get("raw_output", ""),
        )

    with st.container():
        render_trace(result.get("trace", []))
        render_interactive_flow()
        render_agents_debug(result.get("agents", []))
else:
    st.info("Enter a Project ID and click **Run** to fetch data.")
