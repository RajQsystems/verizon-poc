import streamlit as st
import pandas as pd
import plotly.express as px
from pyvis.network import Network
import streamlit.components.v1 as components
import requests
import sys, os
from dotenv import load_dotenv
load_dotenv()
# add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agentic_ai.src.role_based_agents.crews.role_summary.config.mapper import get_agent_details, get_task_details

BASE_URL = os.getenv("BASE_URL")
API_BASE = f"{BASE_URL}/api/v1"
# API_BASE = f"http://localhost:8000/api/v1"

st.set_page_config(page_title="Role-Centric Agent View", layout="wide")
st.title("👷 Role-Centric View — Agent Performance")

# ----------------------
# Fetch available roles
# ----------------------
try:
    roles_resp = requests.get(f"{API_BASE}/alerts/agents/all")
    roles_data = roles_resp.json().get("agents", [])
    role_names = [r["name"] for r in roles_data]
except Exception as e:
    st.error(f"Could not fetch roles: {e}")
    role_names = []

# ----------------------
# Filters
# ----------------------
col1 = st.container()
with col1:
    role = st.selectbox("Select Agent Role", role_names, index=0 if role_names else None)

# move button down below nicely
st.markdown("")
run_clicked = st.button("Run Role View", use_container_width=False)

st.markdown("---")

# ----------------------
# Helper to render Agent & Task breakdown
# ----------------------
def render_agent_breakdown(task_key, task_title, agents_list, captured_output):
    task_info = get_task_details(task_key)
    agent_key = task_info.get("agent") or ""
    agent_info = get_agent_details(agent_key)

    # Match the agent output from API debug info
    match = next((a for a in agents_list if a.get("task_key") == task_key), None)

    with st.expander(f"{agent_info.get('role','Unknown Agent')} — {task_title}"):
        st.markdown("**Task Details**")
        st.json(task_info)

        st.markdown("**Agent Details**")
        st.json(agent_info)

        st.markdown("**Captured Output**")
        if match and (match.get("output_raw") or match.get("output_json")):
            st.json(match.get("output_raw") or match.get("output_json"))
        else:
            st.json(captured_output)


# ----------------------
# Run if clicked
# ----------------------
if run_clicked and role:
    with st.spinner("⏳ Hold on... Processing role data. This may take up to a minute."):
        role_resp = requests.get(f"{API_BASE}/alerts/{role}")
        summary_resp = requests.get(f"{API_BASE}/common/role/summary/{role}")

    if role_resp.status_code != 200 or summary_resp.status_code != 200:
        st.error("⚠️ Could not fetch role data from backend.")
    else:
        role_data = role_resp.json()
        summary_data = summary_resp.json()

        # Convert sections into DataFrames
        status_df = pd.DataFrame(role_data.get("status", {}).get("distribution", []))
        delays_df = pd.DataFrame(role_data.get("delays", []))
        anomalies_df = pd.DataFrame(role_data.get("anomalies", []))
        impacts_df = pd.DataFrame(role_data.get("impacts", []))
        dependencies = role_data.get("dependencies", [])
        agents_debug = summary_data.get("agents", [])

        # ----------------------
        # Summary Header
        # ----------------------
        st.markdown(f"## 📝 Summary for {role}")
        # st.markdown(f"### {summary_data.get('headline','')}")

        # ----------------------
        # Tabs
        # ----------------------
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            ["📊 Status", "⏱ Delays", "⚠️ Anomalies", "🚧 Impacted Projects", "🔗 Dependencies", "📑 Executive Summary"]
        )

        # --- Status ---
        with tab1:
            st.subheader(f"Status Distribution for {role}")
            if not status_df.empty:
                fig = px.bar(status_df, x="status", y="count", color="status", text_auto=True)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(status_df)
            else:
                st.info("No status data available.")

            st.subheader("🔍 Agent & Task Breakdown")
            render_agent_breakdown(
                "status_summary_task",
                "Status Summary",
                agents_debug,
                role_data.get("status", {})
            )

        # --- Delays ---
        with tab2:
            st.subheader("Planned vs Actual Delays")
            if not delays_df.empty:
                delays_df["delay_days"] = delays_df["delay_days"].fillna(0)
                fig2 = px.bar(delays_df, x="project_id", y="delay_days", text_auto=True)
                st.plotly_chart(fig2, use_container_width=True)
                st.dataframe(delays_df)
            else:
                st.info("No delay data available.")

            st.subheader("🔍 Agent & Task Breakdown")
            render_agent_breakdown(
                "delay_analysis_task",
                "Delay Analysis",
                agents_debug,
                role_data.get("delays", [])
            )

        # --- Anomalies ---
        with tab3:
            st.subheader("Anomalies Linked to Role")
            if not anomalies_df.empty:
                st.dataframe(anomalies_df)
            else:
                st.info("No anomalies found.")

            st.subheader("🔍 Agent & Task Breakdown")
            render_agent_breakdown(
                "anomaly_triage_task",
                "Anomaly Triage",
                agents_debug,
                role_data.get("anomalies", [])
            )

        # --- Impacted Projects ---
        with tab4:
            st.subheader("Projects Impacted by Role")
            if not impacts_df.empty:
                fig3 = px.bar(
                    impacts_df,
                    x="project_id",
                    y="delayed_milestones",
                    color="delayed_milestones",
                    text_auto=True,
                )
                st.plotly_chart(fig3, use_container_width=True)
                st.dataframe(impacts_df)
            else:
                st.info("No impacted projects available.")

            st.subheader("🔍 Agent & Task Breakdown")
            render_agent_breakdown(
                "vendor_attribution_task",
                "Vendor Attribution",
                agents_debug,
                role_data.get("impacts", [])
            )

        # --- Dependencies ---
        with tab5:
            st.subheader("Dependency Graph")
            if dependencies:
                # Map IDs → milestone names if available
                milestone_map = {i: f"{d.get('milestone','Milestone')}" for i, d in enumerate(role_data.get("delays", []), start=1)}

                net = Network(height="800px", width="100%", directed=True, notebook=False)
                for dep in dependencies:
                    from_label = milestone_map.get(dep["from"], str(dep["from"]))
                    to_label = milestone_map.get(dep["to"], str(dep["to"]))
                    net.add_node(from_label, label=from_label)
                    net.add_node(to_label, label=to_label)
                    net.add_edge(from_label, to_label)
                net.save_graph("role_graph.html")
                with open("role_graph.html", "r", encoding="utf-8") as f:
                    html = f.read()
                components.html(html, height=800)
            else:
                st.info("No dependencies found.")

            st.subheader("🔍 Agent & Task Breakdown")
            render_agent_breakdown(
                "dependency_task",
                "Dependency Mapping",
                agents_debug,
                role_data.get("dependencies", [])
            )

        # --- Executive-Level Summary ---
        with tab6:
            st.subheader("📑 Executive Summary")
            st.markdown(f"### {summary_data.get('headline','')}")
            st.markdown("**Top Risks:**")
            for r in summary_data.get("risks", []):
                st.markdown(f"- {r}")
            st.markdown("**Next Actions:**")
            for a in summary_data.get("actions", []):
                st.markdown(f"- {a.get('action') if isinstance(a,dict) else a}")

            st.subheader("🔍 Agent & Task Breakdown")
            render_agent_breakdown(
                "final_composition_task",
                "Final Composition",
                agents_debug,
                {
                    "headline": summary_data.get("headline",""),
                    "risks": summary_data.get("risks", []),
                    "next_actions": summary_data.get("actions", [])
                }
            )
