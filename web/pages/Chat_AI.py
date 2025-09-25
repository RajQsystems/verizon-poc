import requests
import streamlit as st
import os
from utils.response_builder import display_response
from dotenv import load_dotenv
from utils.sidebar_logo import add_sidebar_logo

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
API_URL = f"{BASE_URL}/api/v1/query"

# =========================
# Sidebar Logo
# =========================
add_sidebar_logo()


@st.cache_data(ttl=300)
def fetch_data(user_query: str = ""):
    payload = {"user_query": user_query}
    headers = {"Content-Type": "application/json"}

    r = requests.post(API_URL, json=payload, headers=headers, timeout=300)
    r.raise_for_status()
    return r.json()


# Page configuration
st.set_page_config(
    page_title="AI Chat",
    page_icon="🤖",
    layout="centered",
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

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title
st.title("🤖 Agentic Assistant")
st.caption("Ask me anything and I'll try to help")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("is_code", False):
            st.code(message["content"], language="text")
        elif message["role"] == "assistant" and isinstance(message["content"], dict):
            st.markdown(message["content"]["summary"])
            if message["content"]["df"] is not None:
                st.dataframe(message["content"]["df"], use_container_width=True)
        else:
            st.markdown(message["content"])

# User input
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking ⏳")

        # Default assistant response
        assistant_content = None

        if "hello" in prompt.lower():
            assistant_content = "Hello there👋!"
        else:
            # Read JSON and generate structured response
            response = fetch_data(prompt)
            if response:
                summary, table = display_response(response)
                assistant_content = {"summary": summary, "df": table}
            else:
                assistant_content = f"I received your message: _{prompt}_"

        # Clear the "Thinking" placeholder
        message_placeholder.empty()  # <-- This removes the "Thinking ⏳" text

        # Render the response
        if isinstance(assistant_content, dict):
            st.markdown(assistant_content["summary"])
            if assistant_content["df"] is not None:
                st.dataframe(assistant_content["df"], use_container_width=True)
        else:
            st.markdown(assistant_content)

        # Store in session state
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_content}
        )
