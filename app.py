"""
Streamlit UI for Social-to-Lead Agentic Workflow
Inflix AI Assistant - Powered by Google Gemini + RAG
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Inflix AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check for Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found. Please add it to your .env file.")
    st.info("Get your free API key at: https://aistudio.google.com")
    st.code("GEMINI_API_KEY=your-key-here", language="bash")
    st.stop()

# Import agent after env check
from agent.orchestrator import AgentOrchestrator

# Initialize orchestrator
@st.cache_resource
def get_orchestrator():
    return AgentOrchestrator()

orchestrator = get_orchestrator()

# Sidebar
with st.sidebar:
    st.title("Inflix AI Assistant")
    st.markdown("---")

    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("Captured Leads")
    leads_count = orchestrator.lead_capture_tool.get_leads_summary()["total_leads"]
    st.metric("Leads", leads_count)

    st.markdown("---")
    st.subheader("Sample Questions")
    sample_questions = [
        "What does Inflix do?",
        "How much does it cost?",
        "Does it work with Instagram?",
        "I want to try it for my business",
        "I'm ready to sign up!"
    ]
    for question in sample_questions:
        if st.button(question, use_container_width=True, key=f"sample_{question}"):
            st.session_state.pending_message = question

# Main chat area
st.title("Inflix AI Assistant")
st.caption("Social-to-Lead Agentic Workflow | Powered by Gemini + RAG")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_message" not in st.session_state:
    st.session_state.pending_message = None

# Metrics row
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Leads Captured", orchestrator.lead_capture_tool.get_leads_summary()["total_leads"])
with col2:
    st.metric("Messages", len(st.session_state.messages))
with col3:
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    st.metric("Model", model_name)

st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])
        if message.get("intent"):
            st.caption(f"Intent: {message['intent']}")

# Handle pending message from sidebar buttons
if st.session_state.pending_message:
    user_input = st.session_state.pending_message
    st.session_state.pending_message = None
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            result = orchestrator.process_message(user_input)
            response = result.get("message", result.get("response", "Sorry, I could not process that."))
            intent = result.get("intent", "unknown")
        st.markdown(response)
        st.caption(f"Intent: {intent}")
    st.session_state.messages.append({"role": "assistant", "content": response, "intent": intent})
    st.rerun()

# Chat input
user_input = st.chat_input("Ask me about Inflix...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            result = orchestrator.process_message(user_input)
            response = result.get("message", result.get("response", "Sorry, I could not process that."))
            intent = result.get("intent", "unknown")
        st.markdown(response)
        st.caption(f"Intent: {intent}")
    st.session_state.messages.append({"role": "assistant", "content": response, "intent": intent})
    st.rerun()
