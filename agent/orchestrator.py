"""
Agent Orchestrator - Main agent loop that coordinates all components
for the Social-to-Lead Agentic Workflow.
"""

import os
import logging
from typing import Optional
from datetime import datetime

from agent.intent_detector import IntentDetector, IntentLevel
from agent.response_generator import ResponseGenerator
from rag.retriever import RAGRetriever
from tools.lead_capture import LeadCaptureTool
from tools.pricing_tool import PricingTool
from tools.booking_tool import BookingTool

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Main orchestrator for the Social-to-Lead Agentic Workflow.
    
    Coordinates:
    - Intent detection
    - RAG-based product Q&A
    - Tool execution (lead capture, pricing, booking)
    - Conversation history management
    """
    
    def __init__(self):
        self.intent_detector = IntentDetector()
        self.rag_retriever = RAGRetriever()
        self.response_generator = ResponseGenerator()
        self.lead_capture_tool = LeadCaptureTool()
        self.pricing_tool = PricingTool()
        self.booking_tool = BookingTool()
        
        self.conversation_history = []
        self.current_lead_info = {}
        self.lead_capture_stage = None  # None, 'asking_name', 'asking_email', 'asking_company'
        
        logger.info("AgentOrchestrator initialized successfully")
    
    def process_message(self, user_message: str) -> dict:
        """
        Process a user message through the full agentic pipeline.
        
        Args:
            user_message: The user's input message
            
        Returns:
            dict with keys: message, intent, tools_used, lead_captured
        """
        tools_used = []
        lead_captured = None
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Handle lead capture flow if in progress
        if self.lead_capture_stage:
            response, lead_captured = self._handle_lead_capture_flow(user_message)
            intent = IntentLevel.HIGH_INTENT
            if lead_captured:
                tools_used.append("lead_capture")
        else:
            # Step 1: Detect intent
            intent = self.intent_detector.detect(user_message, self.conversation_history)
            logger.info(f"Detected intent: {intent}")
            
            # Step 2: Retrieve relevant context via RAG
            rag_context = self.rag_retriever.retrieve(user_message)
            
            # Step 3: Determine which tools to invoke based on intent
            tool_results = {}
            
            if intent == IntentLevel.READY_TO_BUY or intent == IntentLevel.HIGH_INTENT:
                # Start lead capture flow
                self.lead_capture_stage = 'asking_name'
                response = self._generate_lead_capture_prompt(rag_context, intent)
                tools_used.append("lead_capture_initiated")
                
            elif intent == IntentLevel.INTERESTED:
                # Show pricing information
                pricing_info = self.pricing_tool.get_pricing()
                tool_results["pricing"] = pricing_info
                tools_used.append("pricing_tool")
                response = self.response_generator.generate(
                    user_message, rag_context, self.conversation_history, 
                    intent, tool_results
                )
                
            else:
                # BROWSING or CURIOUS - just answer with RAG
                response = self.response_generator.generate(
                    user_message, rag_context, self.conversation_history,
                    intent, tool_results
                )
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "message": response,
            "intent": intent.value if hasattr(intent, 'value') else str(intent),
            "tools_used": tools_used,
            "lead_captured": lead_captured
        }
    
    def _generate_lead_capture_prompt(self, rag_context: str, intent: IntentLevel) -> str:
        """Generate a response that transitions into lead capture."""
        base_response = self.response_generator.generate(
            "The user is showing high purchase intent", 
            rag_context, self.conversation_history, intent, {}
        )
        return (base_response + 
                "\n\nI'd love to help you get started with Inflix! "
                "Could I get your **name** first?")
    
    def _handle_lead_capture_flow(self, user_message: str):
        """Handle the multi-turn lead capture conversation flow."""
        lead_captured = None
        
        if self.lead_capture_stage == 'asking_name':
            self.current_lead_info['name'] = user_message.strip()
            self.lead_capture_stage = 'asking_email'
            response = f"Great to meet you, {self.current_lead_info['name']}! What's your **email address**?"
            
        elif self.lead_capture_stage == 'asking_email':
            self.current_lead_info['email'] = user_message.strip()
            self.lead_capture_stage = 'asking_company'
            response = "Thanks! And what **company** are you from? (or 'solo' if you're an individual)"
            
        elif self.lead_capture_stage == 'asking_company':
            self.current_lead_info['company'] = user_message.strip()
            
            # Save the lead
            lead_data = {
                **self.current_lead_info,
                "intent": "HIGH_INTENT",
                "conversation_summary": self._summarize_conversation(),
                "timestamp": datetime.now().isoformat()
            }
            saved_lead = self.lead_capture_tool.capture_lead(lead_data)
            lead_captured = saved_lead
            
            # Try to book a demo
            booking_info = self.booking_tool.schedule_demo(
                self.current_lead_info.get('name', ''),
                self.current_lead_info.get('email', '')
            )
            
            response = (
                f"🎉 Perfect! I've captured your details, **{self.current_lead_info['name']}**!\n\n"
                f"Our team will reach out to you at **{self.current_lead_info['email']}** within 24 hours.\n\n"
                f"{booking_info}\n\n"
                "In the meantime, feel free to ask me anything else about Inflix!"
            )
            
            # Reset lead capture state
            self.lead_capture_stage = None
            self.current_lead_info = {}
        else:
            response = "I'm sorry, something went wrong. Let me start over. What can I help you with?"
            self.lead_capture_stage = None
            self.current_lead_info = {}
        
        return response, lead_captured
    
    def _summarize_conversation(self) -> str:
        """Create a brief summary of the conversation for the lead record."""
        user_messages = [
            msg["content"] for msg in self.conversation_history 
            if msg["role"] == "user"
        ]
        if user_messages:
            return " | ".join(user_messages[-3:])  # Last 3 user messages
        return "No conversation history"
    
    def get_captured_leads(self) -> list:
        """Get all captured leads."""
        return self.lead_capture_tool.get_all_leads()
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        self.current_lead_info = {}
        self.lead_capture_stage = None
        logger.info("Conversation reset")
