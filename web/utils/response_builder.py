import streamlit as st
import pandas as pd


def display_response(data):
    # Extract summary
    summary = data.get("summary", "No summary available.")

    # Extract table data
    table_data = data.get("data", {})
    df = None
    if table_data and "rows" in table_data and "columns" in table_data:
        df = pd.DataFrame(table_data["rows"], columns=table_data["columns"])

    # Return both summary and df instead of directly rendering
    return summary, df
