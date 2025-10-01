# Agentic_AI.py

import requests
import streamlit as st
import os
import pandas as pd
import altair as alt
from utils.response_builder import display_response
from dotenv import load_dotenv
from utils.sidebar_logo import add_sidebar_logo

# =========================
# Load environment + API
# =========================
load_dotenv()
BASE_URL = os.getenv("BASE_URL")
API_URL = "http://localhost:8000/api/v1/query"  # fallback to localhost for dev

# =========================
# Sidebar Logo
# =========================
add_sidebar_logo()

# =========================
# Data Fetching
# =========================
@st.cache_data(ttl=300)
def fetch_data(user_query: str = ""):
    payload = {"user_query": user_query}
    headers = {"Content-Type": "application/json"}
    r = requests.post(API_URL, json=payload, headers=headers, timeout=300)
    r.raise_for_status()
    return r.json()


# =========================
# Smart Chart Selector
# =========================
def choose_chart(user_query: str, df: pd.DataFrame):
    """
    Selects the most relevant chart type based on user query intent + dataframe schema.
    """
    if df is None or df.empty:
        return None

    # Identify column types
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
    categorical_cols = [c for c in df.columns if c not in numeric_cols + datetime_cols]

    query_lower = user_query.lower()

    # ---- Pie Chart Cases ----
    if "share" in query_lower or "distribution" in query_lower or "proportion" in query_lower:
        if numeric_cols and categorical_cols:
            return alt.Chart(df).mark_arc().encode(
                theta=alt.Theta(field=numeric_cols[0], type="quantitative"),
                color=alt.Color(field=categorical_cols[0], type="nominal"),
                tooltip=categorical_cols + numeric_cols,
            )

    # ---- Line Chart Cases (time series) ----
    if "trend" in query_lower or "per month" in query_lower or "time" in query_lower or "quarter" in query_lower or datetime_cols:
        if datetime_cols and numeric_cols:
            return alt.Chart(df).mark_line(point=True).encode(
                x=alt.X(datetime_cols[0], type="temporal"),
                y=alt.Y(numeric_cols[0], type="quantitative"),
                color=alt.value("steelblue"),
                tooltip=datetime_cols + numeric_cols,
            )

    # ---- Bar Chart Cases ----
    if "count" in query_lower or "how many" in query_lower or "top" in query_lower or "longest" in query_lower or categorical_cols:
        if numeric_cols and categorical_cols:
            return alt.Chart(df).mark_bar().encode(
                x=alt.X(categorical_cols[0], type="nominal", sort="-y"),
                y=alt.Y(numeric_cols[0], type="quantitative"),
                color=alt.Color(categorical_cols[0], type="nominal"),
                tooltip=categorical_cols + numeric_cols,
            )

    # ---- Fallback scatter ----
    if len(numeric_cols) >= 2:
        return alt.Chart(df).mark_circle(size=60).encode(
            x=numeric_cols[0],
            y=numeric_cols[1],
            tooltip=df.columns.tolist(),
        )

    return None


# =========================
# Helper: Dynamic Visualization + Trace
# =========================
def render_results(user_query: str, content: dict):
    summary = content.get("summary", "")
    df = content.get("df", None)
    trace = content.get("trace", [])

    # --- Top Row: Summary + Execution Trace ---
    top_left, top_right = st.columns([2, 1])

    with top_left:
        st.markdown("### 📊 Summary")
        st.markdown(summary)

        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)

    with top_right:
        if trace:
            st.markdown("### ⚙️ Execution Trace")

            # Step renaming map
            step_name_map = {
                "read_table_description": "Analyze User Query",
                "generate_sql_query": "Generate Relevant Information",
                "run_sql_query": "Run Agentic Process",
                "interpret_result": "Interpret Overall Result",
            }

            for i, step in enumerate(trace, 1):
                raw_step = step.get("step", "")
                display_step = step_name_map.get(raw_step, raw_step)

                with st.expander(f"Step {i}: {display_step}"):
                    if step.get("time"):
                        st.caption(f"⏱ {step['time']}")
                    st.write(step.get("message", ""))
                    if step.get("payload"):
                        st.json(step["payload"])

    # --- Visualization ---
    st.markdown("### 📈 Visualization")
    if df is not None and not df.empty:
        chart = choose_chart(user_query, df)
        if chart:
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("ℹ️ No suitable chart found for this query.")
    else:
        st.info("No results to visualize.")


# =========================
# Page configuration
# =========================
st.set_page_config(
    page_title="AI Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# Chat State
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# Page Title
# =========================
st.title("🤖 Agentic Assistant")
st.caption("Ask me anything and I'll generate queries + charts")


# =========================
# Display Chat Messages
# =========================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("is_code", False):
            st.code(message["content"], language="text")
        elif message["role"] == "assistant" and isinstance(message["content"], dict):
            render_results(message.get("query", ""), message["content"])
        else:
            st.markdown(message["content"])


# =========================
# User Input
# =========================
if prompt := st.chat_input("Type your message here..."):
    # Store user input
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking ⏳")

        try:
            response = fetch_data(prompt)
            summary, table, trace = display_response(response)
            assistant_content = {"summary": summary, "df": table, "trace": trace}
        except Exception as e:
            assistant_content = f"⚠️ Error: {e}"

        message_placeholder.empty()

        if isinstance(assistant_content, dict):
            render_results(prompt, assistant_content)
        else:
            st.markdown(assistant_content)

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_content, "query": prompt}
        )
