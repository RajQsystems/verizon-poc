import streamlit as st

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
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("is_code", False):
                st.code(message["content"], language="text")
            else:
                st.markdown(message["content"])

# User input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response (LOCAL LOGIC instead of API)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking ⏳")

        # Simple placeholder logic
        if "hello" in prompt.lower():
            assistant_response = "Hello there👋!"
        else:
            assistant_response = f"I received your message: _{prompt}_"

        # Render assistant response
        message_placeholder.markdown(assistant_response, unsafe_allow_html=True)

    # Store assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )
