"""
Response Generator - Generates contextual responses using GPT
based on RAG context, intent level, and conversation history.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

from agent.intent_detector import IntentLevel

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an AI assistant for **Inflix** — an AI-powered social media automation SaaS platform. 
Your role is to help potential customers understand the product, answer their questions, and guide them toward signing up.

About Inflix:
- AI-powered social media scheduling, content generation, and analytics
- Supports Instagram, Twitter/X, LinkedIn, Facebook, TikTok
- Uses AI to generate captions, hashtags, and optimal posting times
- Provides detailed analytics and competitor tracking
- Plans: Starter ($29/mo), Growth ($79/mo), Enterprise (custom)

Guidelines:
- Be friendly, helpful, and professional
- Give concise but complete answers
- Use the provided product documentation context to answer accurately
- If you don't know something, say so honestly
- Never make up features or pricing not in the context
- Tailor your response based on the detected intent level
- For HIGH_INTENT users, naturally transition toward getting their contact info"""

INTENT_INSTRUCTIONS = {
    IntentLevel.BROWSING: "Keep response brief and welcoming. Introduce Inflix at a high level.",
    IntentLevel.CURIOUS: "Answer the question clearly. Highlight one or two compelling features.",
    IntentLevel.INTERESTED: "Give detailed, feature-rich answers. Mention pricing and trial offer.",
    IntentLevel.HIGH_INTENT: "Be enthusiastic. Emphasize value, mention free trial, and guide toward getting started.",
    IntentLevel.READY_TO_BUY: "Express excitement. Make the path to signing up super clear and easy."
}


class ResponseGenerator:
    """
    Generates responses using GPT-4o with RAG context and intent-aware prompting.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    def generate(
        self,
        user_message: str,
        rag_context: str,
        conversation_history: List[Dict],
        intent: IntentLevel,
        tool_results: Dict[str, Any] = None
    ) -> str:
        """
        Generate a response using GPT with full context.
        
        Args:
            user_message: The user's current message
            rag_context: Retrieved product documentation context
            conversation_history: Previous conversation turns
            intent: Detected intent level
            tool_results: Results from any tools that were invoked
            
        Returns:
            Generated response string
        """
        try:
            messages = self._build_messages(
                user_message, rag_context, conversation_history, intent, tool_results
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return self._fallback_response(user_message, intent)
    
    def _build_messages(
        self,
        user_message: str,
        rag_context: str,
        conversation_history: List[Dict],
        intent: IntentLevel,
        tool_results: Dict[str, Any]
    ) -> List[Dict]:
        """Build the message list for the API call."""
        
        # Build context string
        context_parts = []
        
        if rag_context:
            context_parts.append(f"PRODUCT DOCUMENTATION:\n{rag_context}")
        
        if tool_results:
            for tool_name, result in tool_results.items():
                context_parts.append(f"TOOL RESULT ({tool_name}):\n{result}")
        
        intent_instruction = INTENT_INSTRUCTIONS.get(intent, "")
        
        system_message = SYSTEM_PROMPT
        if context_parts:
            system_message += "\n\n" + "\n\n".join(context_parts)
        if intent_instruction:
            system_message += f"\n\nINTENT LEVEL: {intent.value}\nINSTRUCTION: {intent_instruction}"
        
        messages = [{"role": "system", "content": system_message}]
        
        # Add recent conversation history
        for turn in conversation_history[-8:]:  # Last 4 exchanges
            if turn["role"] in ["user", "assistant"]:
                messages.append({
                    "role": turn["role"],
                    "content": turn["content"]
                })
        
        # Add current user message if not already in history
        if not conversation_history or conversation_history[-1].get("content") != user_message:
            messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _fallback_response(self, user_message: str, intent: IntentLevel) -> str:
        """Fallback response when API call fails."""
        return (
            "Thank you for your interest in Inflix! I'm having a brief technical issue. "
            "Please feel free to visit our website at inflix.ai or email us at hello@inflix.ai "
            "and our team will be happy to help you out!"
        )
