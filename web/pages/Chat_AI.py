import streamlit as st
from utils.response_builder import display_response
import json

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
            with open("utils/response.json", "r") as f:
                sample_data = json.load(f)
            if sample_data:
                summary, table = display_response(sample_data)
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
