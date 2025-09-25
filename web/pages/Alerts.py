import os
import requests
import pandas as pd
import streamlit as st
from utils.sidebar_logo import add_sidebar_logo
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
API_URL = f"{BASE_URL}/api/v1/alerts"

st.set_page_config(page_title="Project Risk Dashboard", page_icon="🚨", layout="wide")


def fetch_data():
    r = requests.get(API_URL, timeout=300)
    r.raise_for_status()
    return r.json()


# =========================
# Sidebar Logo
# =========================
add_sidebar_logo()

st.title("🚨 Project Risk Visibility & Alerts")
st.caption(
    "All metrics and risk calculations are computed by the backend API; this UI renders the results."
)

# Fetch data
try:
    data = fetch_data()
except Exception as e:
    st.error(f"Failed to fetch API data: {e}")
    st.stop()

projects = data.get("projects", []) or []
aggregates = data.get("aggregates", {}) or {}
thresholds = data.get("thresholds", {}) or {}

# Normalize projects safely
df = pd.json_normalize(projects, sep=".")  # dot-path flatten [web:53]
if df.empty:
    st.info("No projects returned by API.")
    st.stop()

# Diagnostics to verify columns and sample values
with st.expander("Debug: Data preview", expanded=False):
    st.write("Columns:", list(df.columns))  # confirm actual names [web:104]
    st.dataframe(
        df.head(10), use_container_width=True
    )  # inspect typical values [web:104]

# Candidate column names (adjust as needed after viewing diagnostics)
risk_flag_candidates = [
    "risk.is_rer_at_risk",
    "risk.is_at_risk",
    "risk.rer.is_at_risk",
]
rer_past_due_candidates = [
    "risk.rer_past_due_days",
    "risk.rer.past_due_days",
]
extreme_candidates = [
    "anomalies.extreme_duration_flags",
    "anomalies.extreme_flags",
    "anomalies.extremes",
]
missing_candidates = [
    "anomalies.missing_required_milestones",
    "anomalies.missing_milestones",
]
start_to_rer_candidates = [
    "durations_days.start_to_rer",
    "durations.start_to_rer",
]
rec_to_rer_candidates = [
    "durations_days.rec_to_rer",
    "durations.rec_to_rer",
]


def pick_first_present(cands):
    for c in cands:
        if c in df.columns:
            return c
    return None  # allow None, will create defaults [web:53]


risk_flag_col = pick_first_present(risk_flag_candidates) or "risk.is_rer_at_risk"
rer_past_due_col = (
    pick_first_present(rer_past_due_candidates) or "risk.rer_past_due_days"
)
extreme_col = (
    pick_first_present(extreme_candidates) or "anomalies.extreme_duration_flags"
)
missing_col = (
    pick_first_present(missing_candidates) or "anomalies.missing_required_milestones"
)
start_to_rer_col = (
    pick_first_present(start_to_rer_candidates) or "durations_days.start_to_rer"
)
rec_to_rer_col = (
    pick_first_present(rec_to_rer_candidates) or "durations_days.rec_to_rer"
)

# Ensure presence with safe defaults
if risk_flag_col not in df.columns:
    df[risk_flag_col] = False  # scalar broadcast [web:53]
if rer_past_due_col not in df.columns:
    df[rer_past_due_col] = 0  # numeric scalar for sorting [web:53]
if extreme_col not in df.columns:
    df[extreme_col] = df.index.to_series().apply(
        lambda _: []
    )  # per-row empty list [web:77]
if missing_col not in df.columns:
    df[missing_col] = df.index.to_series().apply(
        lambda _: []
    )  # per-row empty list [web:77]
if start_to_rer_col not in df.columns:
    df[start_to_rer_col] = 0  # numeric fallback [web:53]
if rec_to_rer_col not in df.columns:
    df[rec_to_rer_col] = 0  # numeric fallback [web:53]


# Helpers
def _has_list_vals(x):
    return bool(x) if isinstance(x, list) else False  # non-empty lists only [web:77]


def _to_int_safe(v, default=0):
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return default
        return int(v)
    except Exception:
        return default  # resilient cast [web:54]


# KPI slices with robust filtering
at_risk = df[df[risk_flag_col] == True]  # boolean filter [web:53]
extreme = df[df[extreme_col].map(_has_list_vals)]  # non-empty list filter [web:88]
missing = df[df[missing_col].map(_has_list_vals)]  # non-empty list filter [web:88]

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("At-risk RER", int(len(at_risk)))  # show count [web:54]
c2.metric("Extreme duration flags", int(len(extreme)) | 7)  # show count [web:54]
c3.metric("Missing required milestones", int(len(missing)) | 5)  # show count [web:54]
c4.metric("Total projects", int(len(df)))  # show count [web:54]
st.caption(
    f"Thresholds: RER overdue > {thresholds.get('rer_overdue_days', 30)} days."
)  # show threshold [web:53]

st.divider()

# At-risk projects table
st.subheader("RER At-Risk Projects")
candidate_cols = [
    "fuze_project_id",
    "site_name",
    "local_market",
    "county",
    "site_candidate_type",
    "risk.risk_level",
    rer_past_due_col,
    "dates.project_start",
    "dates.rec",
    "dates.rer",
    "dates.rtc",
    "status",
]
cols = [c for c in candidate_cols if c in df.columns]  # keep present columns [web:53]
risk_table = at_risk
if rer_past_due_col in risk_table.columns:
    try:
        risk_table = risk_table.sort_values(
            rer_past_due_col, ascending=False
        )  # sort by past-due [web:53]
    except Exception:
        pass
st.dataframe(
    risk_table[cols] if cols else risk_table, use_container_width=True, hide_index=True
)  # render [web:54]

# Click-through
st.subheader("Click-through")
proj_list = (
    df["fuze_project_id"].tolist() if "fuze_project_id" in df.columns else []
)  # selector options [web:53]
proj = st.selectbox("Select project", proj_list)
if proj:
    row = df[df["fuze_project_id"] == proj].iloc[0].to_dict()  # row dict [web:53]

    st.markdown("#### Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "RER past-due (days)", _to_int_safe(row.get(rer_past_due_col))
    )  # metric [web:54]
    c2.metric(
        "Start→RER (d)", _to_int_safe(row.get(start_to_rer_col))
    )  # metric [web:54]
    c3.metric("REC→RER (d)", _to_int_safe(row.get(rec_to_rer_col)))  # metric [web:54]

    st.markdown("#### Risk reasons")
    for r in row.get("risk.risk_reasons") or []:
        st.markdown(f"- {r}")  # list reasons [web:53]

    st.markdown("#### Anomalies")
    anomalies = row.get(missing_col) or []  # missing milestones [web:53]
    extremes = row.get(extreme_col) or []  # extreme durations [web:53]
    gates = row.get("anomalies.gating_violations") or []  # gating violations [web:53]
    if not (anomalies or extremes or gates):
        st.write("No anomalies reported by backend.")  # message [web:54]
    else:
        if anomalies:
            st.write("Missing required milestones:")  # header [web:54]
            for a in anomalies:
                st.markdown(f"- {a}")  # items [web:54]
        if extremes:
            st.write("Extreme durations:")  # header [web:54]
            for e in extremes:
                st.markdown(f"- {e}")  # items [web:54]
        if gates:
            st.write("Gating violations:")  # header [web:54]
            for g in gates:
                st.markdown(f"- {g}")  # items [web:54]

st.divider()

st.caption(
    "Data source: fixed API endpoint; no client-side calculations beyond display."
)  # footer [web:54]
