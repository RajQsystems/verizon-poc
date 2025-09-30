import streamlit as st
import pandas as pd


def display_response(data):
    """
    Transform the raw response payload into:
      - summary text
      - pandas DataFrame for tabular results
      - execution trace (list of steps with message + payload)
    """

    # Extract summary
    summary = data.get("summary", "No summary available.")

    # Extract table data
    table_data = data.get("data", {})
    df = None
    if table_data and "rows" in table_data:
        # If backend provided explicit "columns"
        if "columns" in table_data:
            df = pd.DataFrame(table_data["rows"], columns=table_data["columns"])
        else:
            df = pd.DataFrame(table_data["rows"])

    # Extract execution trace
    trace = data.get("trace", [])

    # Return structured tuple for frontend
    return summary, df, trace


def render_response(summary, df, trace):
    """
    Render the response into the Streamlit UI.
    """

    # Show summary
    st.subheader("📊 Summary")
    st.write(summary)

    # Show table if available
    if df is not None and not df.empty:
        st.dataframe(df)

    # Show trace if available
    if trace:
        st.subheader("⚙️ Execution Trace")
        for step in trace:
            with st.expander(f"{step.get('time', '')} — {step.get('step', '')}"):
                st.write(step.get("message", ""))
                payload = step.get("payload", {})
                if payload:
                    st.json(payload)
