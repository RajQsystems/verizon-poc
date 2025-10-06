from datetime import datetime
import os
import sys

import requests
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import pandas as pd
import altair as alt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agentic_ai.mapper import TASKS, AGENTS
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_BASE = f"{BASE_URL}/api/v1"
# API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Agentic Project Summary", page_icon="📊", layout="wide")
st.title("📊 Agentic Project Summary — Live Run Viewer")

# ------------------------
# Main Run Input (moved from sidebar to main)
# ------------------------
# st.markdown("Enter a Project ID and click **Run** to fetch data.")

with st.container():
    col1, col2 = st.columns([3, 1])  # input + button layout
    with col1:
        project_id = st.text_input(
            "Project ID", value="ID_277EA56BE3", label_visibility="collapsed"
        )
    with col2:
        run_btn = st.button("Run", use_container_width=True)


# ------------------------
# Helpers
# ------------------------
def call_json(url: str):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return r.json()


def render_overview(overview: dict):
    with st.expander("Overview", expanded=True):
        ####################
        ##### PROJECTS #####
        ####################
        st.subheader("Project")
        # Convert to datetime
        project = overview.get("project", {})
        project["start_date"] = pd.to_datetime(project["start_date"])
        project["end_date_planned"] = pd.to_datetime(project["end_date_planned"])
        project["end_date_actual"] = pd.to_datetime(project["end_date_actual"])

        # Display project info as card
        st.markdown(f"""
        <div style='padding:20px; border-radius:15px; background-color:#e3f2fd; box-shadow:0 3px 6px rgba(0,0,0,0.1);'>
            <h3>📌 Project Overview: {project["project_id"]}</h3>
            <p><b>Market:</b> {project["market"]}</p>
            <p><b>Site Type:</b> {project["site_type"]}</p>
            <p><b>Start Date:</b> {project["start_date"].date()}</p>
            <p><b>Planned End Date:</b> {project["end_date_planned"].date()}</p>
            <p><b>Actual End Date:</b> {project["end_date_actual"].date()}</p>
            <p><b>Status:</b> {"✅ On Time" if project["end_date_actual"] <= project["end_date_planned"] else "⏰ Delayed"}</p>
        </div>
        """, unsafe_allow_html=True)
        st.text("")

        ######################
        ##### MILESTONES #####
        ######################
        ms = overview.get("milestones", {})
        st.subheader("Milestones")
        st.write(f"Total: **{ms.get('total')}**, Delayed: **{ms.get('delayed')}**")
        with st.expander("Healthy Milestones"):
            tabs = st.tabs(["💼 Business View", "🧩 Raw View"])

            healthy_milestones = ms.get("healthy_milestones", [])
            df = pd.DataFrame(healthy_milestones)
            df["planned_date"] = pd.to_datetime(df["planned_date"])
            df["actual_date"] = pd.to_datetime(df["actual_date"])

            with tabs[0]:
                # ---------- FILTERS ----------
                st.sidebar.header("🔍 Healthy Milestones Filters")
                status_filter = st.sidebar.multiselect(
                    "Filter by Status",
                    options=df["status"].unique(),
                    default=df["status"].unique()
                )
                month_filter = st.sidebar.slider(
                    "Filter by Planned Month Range",
                    min_value=df["planned_date"].min().month,
                    max_value=df["planned_date"].max().month,
                    value=(df["planned_date"].min().month, df["planned_date"].max().month)
                )

                filtered_df = df[
                    (df["status"].isin(status_filter)) &
                    (df["planned_date"].dt.month.between(month_filter[0], month_filter[1]))
                ]

                # ---------- KPI METRICS ----------
                col1, col2, col3 = st.columns(3)
                col1.metric("✅ Completed", len(df[df.status == "Complete"]))
                col2.metric("🚧 In Progress", len(df[df.status == "In Progress"]))
                avg_delay = df["duration_days"].mean()
                col3.metric("📅 Avg Schedule Variance", f"{avg_delay:.1f} days", 
                            delta=None if avg_delay == 0 else f"{'Early' if avg_delay < 0 else 'Late'}")

                st.markdown("---")

                # ---------- TIMELINE CHART ----------
                st.subheader("📅 Milestone Timeline")
                timeline_chart = (
                    alt.Chart(filtered_df)
                    .mark_bar(size=20)
                    .encode(
                        x=alt.X("planned_date:T", title="Planned Date"),
                        x2="actual_date:T",
                        y=alt.Y("name:N", title="Milestone"),
                        color=alt.Color("status:N", scale=alt.Scale(domain=["Complete", "In Progress"], range=["#4CAF50", "#FFC107"])),
                        tooltip=["name", "planned_date", "actual_date", "status", "duration_days"]
                    )
                    .properties(height=300)
                )
                st.altair_chart(timeline_chart, use_container_width=True)

                st.markdown("---")

                # ---------- MILESTONE CARDS ----------
                st.subheader("📋 Milestone Details")

                cols_per_row = 3
                for i in range(0, len(filtered_df), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for col, (_, row) in zip(cols, filtered_df.iloc[i:i+cols_per_row].iterrows()):
                        if row.status == "Complete":
                            color = "#d1e7dd"  # green
                            emoji = "✅"
                        else:
                            color = "#fff3cd"  # yellow
                            emoji = "🚧"

                        if row.duration_days < 0:
                            schedule_text = f"{abs(row.duration_days)} days early"
                        elif row.duration_days > 0:
                            schedule_text = f"{row.duration_days} days late"
                        else:
                            schedule_text = "On time"

                        col.markdown(
                            f"""
                            <div style='background-color:{color}; padding:15px; border-radius:15px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:10px;'>
                                <h4>{emoji} {row.name}</h4>
                                <p><b>Description:</b> {row.description}</p>
                                <p><b>Planned:</b> {row.planned_date.date()}<br>
                                <b>Actual:</b> {row.actual_date.date()}</p>
                                <p><b>Status:</b> {row.status}</p>
                                <p><b>Schedule Impact:</b> {schedule_text}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            
            with tabs[1]:
                st.json(healthy_milestones)

        with st.expander("Delayed Milestones"):
            main_tabs = st.tabs(["💼 Business View", "🧩 Raw View"])

            delayed_milestones = ms.get("delayed_milestones", [])
            df = pd.DataFrame(delayed_milestones)
            df["planned_date"] = pd.to_datetime(df["planned_date"])
            df["actual_date"] = pd.to_datetime(df["actual_date"])

            with main_tabs[0]:
                # --------------------------
                # FILTERS
                # --------------------------
                st.sidebar.header("🔍 Delayed Milestones Filters")
                status_filter = st.sidebar.multiselect(
                    "Filter by Status",
                    options=df["status"].unique(),
                    default=df["status"].unique()
                )
                month_filter = st.sidebar.slider(
                    "Planned Month Range",
                    min_value=int(df["planned_date"].dt.month.min()),
                    max_value=int(df["planned_date"].dt.month.max()),
                    value=(int(df["planned_date"].dt.month.min()), int(df["planned_date"].dt.month.max()))
                )

                filtered_df = df[
                    (df["status"].isin(status_filter)) &
                    (df["planned_date"].dt.month.between(month_filter[0], month_filter[1]))
                ]

                # --------------------------
                # KPIs
                # --------------------------
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("✅ Completed", len(df[df.status == "Complete"]))
                col2.metric("🚧 In Progress", len(df[df.status == "In Progress"]))
                col3.metric("⏰ Delayed", len(df[df.status == "Delayed"]))
                avg_delay = df["duration_days"].dropna().mean()
                col4.metric("📅 Avg Schedule Variance", f"{avg_delay:.1f} days", 
                            delta=None if avg_delay == 0 else f"{'Early' if avg_delay < 0 else 'Late'}")

                st.markdown("---")

                # --------------------------
                # TAB LAYOUT
                # --------------------------
                tabs = st.tabs(["📈 Overview", "🕒 Timeline", "📋 Milestone Details"])

                # -------- OVERVIEW TAB --------
                with tabs[0]:
                    st.subheader("📊 Status Distribution")
                    st.bar_chart(df["status"].value_counts())

                    st.markdown("### Status Summary Table")
                    summary = df.groupby("status").agg(
                        count=("milestone_id", "count"),
                        avg_delay=("duration_days", "mean")
                    ).reset_index()
                    summary["avg_delay"] = summary["avg_delay"].round(1)
                    st.dataframe(summary, use_container_width=True)

                # -------- TIMELINE TAB --------
                with tabs[1]:
                    st.subheader("📅 Milestone Timeline (Planned vs Actual)")
                    timeline_chart = (
                        alt.Chart(filtered_df)
                        .mark_bar(size=20)
                        .encode(
                            x=alt.X("planned_date:T", title="Planned Date"),
                            x2="actual_date:T",
                            y=alt.Y("name:N", title="Milestone"),
                            color=alt.Color("status:N", scale=alt.Scale(domain=["Complete","In Progress","Delayed"], range=["#4CAF50","#FFC107","#F44336"])),
                            tooltip=["name","planned_date","actual_date","status","duration_days"]
                        )
                        .properties(height=400)
                    )
                    st.altair_chart(timeline_chart, use_container_width=True)

                # -------- MILESTONE DETAILS TAB --------
                with tabs[2]:
                    st.subheader("📋 Milestone Details")

                    cols_per_row = 3
                    for i in range(0, len(filtered_df), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for col, (_, row) in zip(cols, filtered_df.iloc[i:i+cols_per_row].iterrows()):
                            # Color mapping by status
                            if row.status == "Complete":
                                color = "#d1e7dd"  # green
                                emoji = "✅"
                            elif row.status == "In Progress":
                                color = "#fff3cd"  # yellow
                                emoji = "🚧"
                            else:
                                color = "#f8d7da"  # red
                                emoji = "⏰"

                            if pd.isna(row.actual_date):
                                actual_str = "Not yet completed"
                            else:
                                actual_str = row.actual_date.date()

                            if pd.isna(row.duration_days):
                                schedule_text = "Pending data"
                            elif row.duration_days < 0:
                                schedule_text = f"{abs(row.duration_days)} days early"
                            elif row.duration_days > 0:
                                schedule_text = f"{row.duration_days} days late"
                            else:
                                schedule_text = "On time"

                            col.markdown(
                                f"""
                                <div style='background-color:{color}; padding:15px; border-radius:15px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:10px;'>
                                    <h4>{emoji} {row.name}</h4>
                                    <p><b>Description:</b> {row.description}</p>
                                    <p><b>Planned:</b> {row.planned_date.date()}<br>
                                    <b>Actual:</b> {actual_str}</p>
                                    <p><b>Status:</b> {row.status}</p>
                                    <p><b>Schedule Impact:</b> {schedule_text}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
            
            with main_tabs[1]:
                st.json(delayed_milestones)
        

        #####################
        ##### ANOMALIES #####
        #####################
        st.subheader("Anomalies")
        anomalies = overview.get("anomalies", {})
        st.write(f"Count: **{anomalies.get('count', 0)}**")
        with st.expander("Details"):
            # Loop through each anomaly in the list
            for anomaly in anomalies.get("details", []):
                # Convert detected_on to date
                detected_on = datetime.strptime(anomaly["detected_on"], "%Y-%m-%d %H:%M:%S").date()
                
                # Set card color based on severity
                if anomaly["severity"] == "High":
                    color = "#f8d7da"  # red
                elif anomaly["severity"] == "Medium":
                    color = "#fff3cd"  # yellow
                else:
                    color = "#d1e7dd"  # green
                
                # Display a simple card for each anomaly
                st.markdown(f"""
                <div style='background-color:{color}; padding:15px; border-radius:12px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:10px;'>
                    <h4>⚠️ {anomaly["type"]} ({anomaly["severity"]})</h4>
                    <p><b>Milestone ID:</b> {anomaly["milestone_id"]}</p>
                    <p><b>Description:</b> {anomaly["description"]}</p>
                    <p><b>Detected On:</b> {detected_on}</p>
                </div>
                """, unsafe_allow_html=True)

        ####################
        ###### CYCLES ######
        ####################
        st.subheader("Cycles")
        with st.expander("Cycle Details"):
            cycles = overview.get("cycles", [])

            # Option: whether lower numbers are better (e.g., duration)
            lower_is_better = st.checkbox("Lower is better (shorter/faster is better)", value=True)

            # Helper to format percent
            def fmt_pct(v):
                return f"{v:.1f}%"

            # Loop through cycles (works for single or many)
            for c in cycles:
                planned = c.get("planned", None)
                actual = c.get("actual", None)

                # compute variance if not provided
                variance = c.get("variance")
                if variance is None and planned is not None and actual is not None:
                    variance = actual - planned

                pct_variance = (variance / planned * 100) if (planned and variance is not None) else None

                # Decide status color and text
                if pct_variance is None:
                    status_text = "Data missing"
                    badge_color = "#f0f0f0"
                else:
                    # if lower_is_better: negative pct_variance is GOOD (actual < planned)
                    is_good = (pct_variance < 0) if lower_is_better else (pct_variance > 0)
                    badge_color = "#d1e7dd" if is_good else "#f8d7da"
                    status_text = "Good" if is_good else "Needs attention"

                # Card header
                st.markdown(f"""
                <div style='background:{badge_color}; padding:14px; border-radius:10px; box-shadow:0 1px 4px rgba(0,0,0,0.08);'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                    <strong style='font-size:16px'>🔁 {c.get("label","Cycle")} — ID {c.get("cycle_id")}</strong><br>
                    <small>Agents: {c.get("agent_start_id")} → {c.get("agent_end_id")}</small>
                    </div>
                    <div style='text-align:right'>
                    <div style='font-size:14px; font-weight:600'>{status_text}</div>
                    <div style='font-size:12px; color:#555'>Variance: {variance if variance is not None else '—'}</div>
                    </div>
                </div>
                </div>
                """, unsafe_allow_html=True)

                # KPIs in a row
                k1, k2, k3 = st.columns([1,1,1])
                k1.metric("Planned", planned if planned is not None else "—")
                k2.metric("Actual", actual if actual is not None else "—")
                pct_label = fmt_pct(pct_variance) if pct_variance is not None else "—"
                k3.metric("Variance (%)", pct_label)

                # Small side-by-side bar chart (planned vs actual)
                if planned is not None and actual is not None:
                    df = pd.DataFrame({
                        "type": ["Planned","Actual"],
                        "value": [planned, actual]
                    })
                    chart = (
                        alt.Chart(df)
                        .mark_bar(size=30)
                        .encode(
                            x=alt.X("value:Q", title=None),
                            y=alt.Y("type:N", sort=["Planned","Actual"], title=None),
                            color=alt.Color("type:N", scale=alt.Scale(range=["#4C78A8","#F58518"]), legend=None),
                            tooltip=["type","value"]
                        )
                        .properties(height=80)
                    )
                    st.altair_chart(chart, use_container_width=True)

                # Plain-language interpretation
                if pct_variance is not None:
                    if lower_is_better:
                        if pct_variance < 0:
                            interp = f"Actual is {abs(variance)} fewer than planned ({fmt_pct(abs(pct_variance))} lower) — this is favorable."
                        elif pct_variance > 0:
                            interp = f"Actual is {variance} more than planned ({fmt_pct(abs(pct_variance))} higher) — this is unfavorable."
                        else:
                            interp = "Actual equals planned — on target."
                    else:
                        # higher is better case
                        if pct_variance > 0:
                            interp = f"Actual is {variance} higher than planned ({fmt_pct(abs(pct_variance))} increase) — favorable."
                        elif pct_variance < 0:
                            interp = f"Actual is {abs(variance)} lower than planned ({fmt_pct(abs(pct_variance))} decrease) — unfavorable."
                        else:
                            interp = "Actual equals planned — on target."
                    st.info(interp)

                st.markdown("---")


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
            f"[{evt.get('time', '')}] {evt.get('step', '')} — {evt.get('message', '')}",
            expanded=False,
        ):
            st.json(evt.get("payload", {}))


# ------------------------
# Interactive Flow (PyVis)
# ------------------------
def render_interactive_flow():
    st.subheader("🕸️ Smart Agent-Task Flow")

    net = Network(height="800px", width="100%", directed=True, bgcolor="#222222")
    net.force_atlas_2based(
        gravity=-50, central_gravity=0.02, spring_length=200, spring_strength=0.08
    )

    all_nodes = set()

    for task_key, details in TASKS.items():
        agent_key = details["agent"]

        if task_key not in all_nodes:
            net.add_node(task_key, label=task_key, color="lightblue", shape="box")
            all_nodes.add(task_key)

        if agent_key not in all_nodes:
            net.add_node(
                agent_key, label=agent_key, color="lightgreen", shape="ellipse"
            )
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
            st.json(
                {
                    "current_task": task_key,
                    "description": mapper_task.get("description"),
                    "steps": mapper_task.get("steps"),
                    "expected_output": mapper_task.get("expected_output"),
                    "previous": mapper_task.get("previous"),
                    "next": mapper_task.get("next"),
                    "associated_agent": mapper_task.get("agent"),
                }
            )

            st.markdown("**Agent Details**")
            st.json(
                {
                    "agent_key": agent_key,
                    "role": mapper_agent.get("role"),
                    "goal": mapper_agent.get("goal"),
                    "backstory": mapper_agent.get("backstory"),
                }
            )

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
    left, right = st.columns([5, 2])

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
