import requests
import pandas as pd
import numpy as np
import streamlit as st
import json

st.set_page_config(page_title="Project Risk Dashboard", page_icon="🚨", layout="wide")

API_URL = "https://example.com/api/projects/risk"  # <-- set your fixed endpoint


@st.cache_data(ttl=300)
def fetch_data():
    # r = requests.get(API_URL, timeout=30)
    # r.raise_for_status()
    # return r.json()
    with open("utils/alert_response.json", "r") as f:
        sample_data = json.load(f)
    return sample_data


st.title("🚨 Project Risk Visibility & Alerts")
st.caption(
    "All metrics and risk calculations are computed by the backend API; this UI renders the results."
)

# Fetch
try:
    data = fetch_data()
except Exception as e:
    st.error(f"Failed to fetch API data: {e}")
    st.stop()

projects = data.get("projects", [])
aggregates = data.get("aggregates", {})
thresholds = data.get("thresholds", {})

df = pd.json_normalize(projects)

# KPIs
at_risk = df[df["risk.is_rer_at_risk"] == True]
extreme = df[
    df["anomalies.extreme_duration_flags"].map(
        lambda x: bool(x) if isinstance(x, list) else False
    )
]
missing = df[
    df["anomalies.missing_required_milestones"].map(
        lambda x: bool(x) if isinstance(x, list) else False
    )
]

c1, c2, c3, c4 = st.columns(4)
c1.metric("At-risk RER", len(at_risk))
c2.metric("Extreme duration flags", len(extreme))
c3.metric("Missing required milestones", len(missing))
c4.metric("Total projects", len(df))
st.caption(f"Thresholds: RER overdue > {thresholds.get('rer_overdue_days', 30)} days.")

st.divider()

# Simple filters for viewing (local only)
cols_for_filters = {
    "local_market": "Local Market",
    "county": "County",
    "site_candidate_type": "Site Candidate Type",
}
with st.expander("Filters"):
    view = df.copy()
    for key, label in cols_for_filters.items():
        if key in view.columns:
            options = ["All"] + sorted(view[key].dropna().unique().tolist())
            choice = st.selectbox(label, options, key=f"flt_{key}")
            if choice != "All":
                view = view[view[key] == choice]
        else:
            st.write(f"{label} column not present in API payload.")

# If no filters are applied, use the full dataframe
# 'view' is already set above; no need for an else block here

# At-risk Projects
st.subheader("RER At-Risk Projects")
cols = [
    "fuze_project_id",
    "site_name",
    "local_market",
    "county",
    "site_candidate_type",
    "risk.rer_past_due_days",
    "dates.project_start",
    "dates.rec",
    "dates.rer",
    "dates.rtc",
]
cols = [c for c in cols if c in view.columns]
risk_table = view[
    view.get("risk.is_rer_at_risk", pd.Series(False, index=view.index)) == True
]
risk_table = risk_table[cols].sort_values(
    view.get("risk.rer_past_due_days", pd.Series(0, index=view.index)).name,
    ascending=False,
)
st.dataframe(risk_table, use_container_width=True, hide_index=True)

# Click-through details
st.subheader("Click-through")
proj_list = (
    view["fuze_project_id"].tolist() if "fuze_project_id" in view.columns else []
)
proj = st.selectbox("Select project", proj_list)
if proj:
    row = view[view["fuze_project_id"] == proj].iloc[0].to_dict()

    st.markdown("#### Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("RER past-due (days)", int(row.get("risk.rer_past_due_days") or 0))
    c2.metric("Start→RER (d)", int(row.get("durations_days.start_to_rer") or 0))
    c3.metric("REC→RER (d)", int(row.get("durations_days.rec_to_rer") or 0))

    st.markdown("#### Risk reasons")
    for r in row.get("risk.risk_reasons") or []:
        st.markdown(f"- {r}")

    st.markdown("#### Anomalies")
    anomalies = row.get("anomalies.missing_required_milestones") or []
    extremes = row.get("anomalies.extreme_duration_flags") or []
    gates = row.get("anomalies.gating_violations") or []
    if not (anomalies or extremes or gates):
        st.write("No anomalies reported by backend.")
    else:
        if anomalies:
            st.write("Missing required milestones:")
            for a in anomalies:
                st.markdown(f"- {a}")
        if extremes:
            st.write("Extreme durations:")
            for e in extremes:
                st.markdown(f"- {e}")
        if gates:
            st.write("Gating violations:")
            for g in gates:
                st.markdown(f"- {g}")

st.divider()

# Aggregates (render only)
st.subheader("Vendor / Owner Leaderboards")
agg_vendors = pd.json_normalize(aggregates.get("vendors", []))
agg_owners = pd.json_normalize(aggregates.get("structure_owners", []))

vc1, vc2 = st.columns(2)
with vc1:
    st.caption("Vendors")
    if not agg_vendors.empty:
        st.dataframe(agg_vendors, use_container_width=True, hide_index=True)
    else:
        st.info("No vendor aggregates from backend.")
with vc2:
    st.caption("Structure Owners")
    if not agg_owners.empty:
        st.dataframe(agg_owners, use_container_width=True, hide_index=True)

st.subheader("County: Average Start→RER")
agg_counties = pd.json_normalize(aggregates.get("counties", []))
if not agg_counties.empty:
    st.dataframe(agg_counties, use_container_width=True, hide_index=True)
else:
    st.info("No county aggregates from backend.")

st.caption(
    "Data source: fixed API endpoint; no client-side calculations beyond display."
)
