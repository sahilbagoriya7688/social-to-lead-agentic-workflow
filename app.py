"""
app.py - Streamlit Web UI for the Social-to-Lead Agentic Workflow
Run with: streamlit run app.py
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.orchestrator import AgentOrchestrator

# Page config
st.set_page_config(
    page_title="Inflix AI Assistant",
    page_icon="",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
.stChatMessage { border-radius: 12px; }
.lead-badge { background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
.intent-badge { padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = AgentOrchestrator()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "leads_captured" not in st.session_state:
        st.session_state.leads_captured = 0


def get_intent_color(intent: str) -> str:
    """Get color for intent badge."""
    colors = {
        "BROWSING": "#6c757d",
        "CURIOUS": "#ffc107",
        "INTERESTED": "#17a2b8",
        "HIGH_INTENT": "#fd7e14",
        "READY_TO_BUY": "#28a745"
    }
    return colors.get(intent, "#6c757d")


def main():
    init_session_state()
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(" Inflix AI Assistant")
        st.caption("Social-to-Lead Agentic Workflow | Powered by GPT-4o + RAG")
    with col2:
        leads_count = len(st.session_state.orchestrator.get_captured_leads())
        st.metric("Leads Captured", leads_count)
    
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This demo showcases a **Social-to-Lead Agentic Workflow** for **Inflix**, 
        an AI-powered social media automation SaaS.
        
        **Features:**
        - Intent Detection (5 levels)
        - RAG-powered Product Q&A
        - Automatic Lead Capture
        - Demo Booking Tool
        - Pricing Information Tool
        """)
        
        st.divider()
        
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.orchestrator.reset_conversation()
            st.rerun()
        
        st.divider()
        st.subheader("Captured Leads")
        leads = st.session_state.orchestrator.get_captured_leads()
        if leads:
            for lead in leads:
                st.markdown(f"**{lead.get('name', 'Unknown')}**")
                st.caption(lead.get('email', ''))
                st.caption(f"Intent: {lead.get('intent', '')}")
                st.divider()
        else:
            st.caption("No leads yet. Chat with the agent!")
        
        st.divider()
        st.subheader("Sample Questions")
        sample_questions = [
            "What does Inflix do?",
            "How much does it cost?",
            "Does it work with Instagram?",
            "I want to try it for my business",
            "I'm ready to sign up!"
        ]
        for q in sample_questions:
            if st.button(q, key=f"sample_{q}", use_container_width=True):
                st.session_state._pending_question = q
                st.rerun()
    
    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("intent"):
                color = get_intent_color(msg["intent"])
                st.markdown(
                    f'<span style="background:{color};color:white;padding:2px 8px;border-radius:12px;font-size:11px;">'
                    f'{msg["intent"]}</span>',
                    unsafe_allow_html=True
                )
    
    # Handle pending question from sidebar
    pending = getattr(st.session_state, "_pending_question", None)
    if pending:
        del st.session_state._pending_question
        prompt = pending
    else:
        prompt = st.chat_input("Ask me anything about Inflix...")
    
    if prompt:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Check for OpenAI key
        if not os.getenv("OPENAI_API_KEY"):
            with st.chat_message("assistant"):
                st.error("OPENAI_API_KEY not found. Please add it to your .env file.")
            return
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.orchestrator.process_message(prompt)
            
            st.markdown(response["message"])
            
            # Show intent badge
            intent = response.get("intent", "")
            if intent:
                color = get_intent_color(intent)
                st.markdown(
                    f'<span style="background:{color};color:white;padding:2px 8px;border-radius:12px;font-size:11px;">'
                    f'Intent: {intent}</span>',
                    unsafe_allow_html=True
                )
            
            # Show tools used
            if response.get("tools_used"):
                st.caption(f"Tools: {', '.join(response['tools_used'])}")
            
            # Show lead capture notification
            if response.get("lead_captured"):
                lead = response["lead_captured"]
                st.success(f"Lead captured: {lead.get('name')} ({lead.get('email')})")
        
        # Add to message history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["message"],
            "intent": response.get("intent", ""),
        })
        
        st.rerun()


if __name__ == "__main__":
    main()
