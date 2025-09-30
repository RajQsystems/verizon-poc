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
# Helper: Dynamic Visualization + Trace
# =========================
import graphviz

def render_results(content: dict):
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
                "run_sql_query": "Run Background Checks",
                "interpret_result": "Interpret Overall Result",
            }

            for i, step in enumerate(trace, 1):
                raw_step = step.get("step", "")
                display_step = step_name_map.get(raw_step, raw_step)  # fallback to raw if not mapped

                with st.expander(f"Step {i}: {display_step}"):
                    if step.get("time"):
                        st.caption(f"⏱ {step['time']}")
                    st.write(step.get("message", ""))
                    if step.get("payload"):
                        st.json(step["payload"])


    # --- Bottom Row: Visualizations + Flowchart ---
    bottom_left, bottom_right = st.columns([2, 1])

    with bottom_left:
        if df is not None and not df.empty:
            numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
            non_numeric_cols = [c for c in df.columns if c not in numeric_cols]

            if numeric_cols and non_numeric_cols:
                st.markdown("### 📈 Visualizations")

                x_col = non_numeric_cols[0]
                y_col = numeric_cols[0]

                st.bar_chart(df.set_index(x_col)[y_col])

                pie = alt.Chart(df).mark_arc().encode(
                    theta=alt.Theta(field=y_col, type="quantitative"),
                    color=alt.Color(field=x_col, type="nominal"),
                )
                st.altair_chart(pie, use_container_width=True)
            else:
                st.info("ℹ️ No numeric data found for charts. Showing only table.")
        else:
            st.info("No results to display.")

    # with bottom_right:
        # if trace:
        #     st.markdown("### 🪢 Flowchart")
        #     dot = graphviz.Digraph()

        #     # Use execution trace to auto-generate nodes and edges
        #     prev_step = None
        #     for i, step in enumerate(trace, 1):
        #         step_id = f"step_{i}"
        #         label = f"{i}. {step.get('step','')}"
        #         dot.node(step_id, label, shape="box", style="filled", color="lightgrey")

        #         if prev_step:
        #             dot.edge(prev_step, step_id)
        #         prev_step = step_id

        #     st.graphviz_chart(dot, use_container_width=True)




# =========================
# Page configuration
# =========================
st.set_page_config(
    page_title="AI Chat",
    page_icon="🤖",
    layout="wide",  # ✅ wide layout to fit trace on right-hand side
    initial_sidebar_state="collapsed",
)

# Custom CSS
st.markdown(
    """
<style>    
    .stChatMessage { border-radius: 0.8rem; }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    [data-testid="stChatMessage"][data-messageowner="user"] {
        background-color: #f0f7ff;
        border-right: 4px solid #1e88e5;
        margin-left: 20%;
        text-align: right;
    }
    [data-testid="stChatMessage"][data-messageowner="assistant"] {
        background-color: #f9f9f9;
        border-left: 4px solid #e0e0e0;
        margin-right: 20%;
    }
    .message-avatar { width: 28px; height: 28px; border-radius: 50%; margin-right: 12px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; }
    .user-avatar { background-color: #1e88e5; }
    .assistant-avatar { background-color: #666; }
    .chat-container { padding-bottom: 100px; }
</style>
""",
    unsafe_allow_html=True,
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
st.caption("Ask me anything and I'll try to help")


# =========================
# Display Chat Messages
# =========================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("is_code", False):
            st.code(message["content"], language="text")
        elif message["role"] == "assistant" and isinstance(message["content"], dict):
            render_results(message["content"])
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

        # Fetch backend response
        response = fetch_data(prompt)
        if response:
            summary, table, trace = display_response(response)
            assistant_content = {"summary": summary, "df": table, "trace": trace}
        else:
            assistant_content = f"I received your message: _{prompt}_"

        message_placeholder.empty()

        if isinstance(assistant_content, dict):
            render_results(assistant_content)
        else:
            st.markdown(assistant_content)

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_content}
        )
