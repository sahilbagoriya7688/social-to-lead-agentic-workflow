"""
Response Generator - Generates contextual responses using Google Gemini API
based on RAG context, intent level, and conversation history.
"""

import os
import logging
from typing import List, Dict, Any
import google.generativeai as genai

from agent.intent_detector import IntentLevel

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an AI assistant for Inflix, an AI-powered social media automation SaaS platform.
Your role is to help potential customers understand the product, answer their questions, and guide them toward signing up.

About Inflix:
- AI-powered social media scheduling, content generation, and analytics
- Supports Instagram, Twitter/X, LinkedIn, Facebook, TikTok
- Uses AI to generate captions, hashtags, and optimal posting times
- Provides detailed analytics and competitor tracking
- Plans: Starter ($29/mo), Growth ($79/mo), Enterprise (custom)
- 14-day free trial on all plans, no credit card required

Guidelines:
- Be friendly, helpful, and professional
- Give concise but complete answers
- Use the provided product documentation context to answer accurately
- If you don't know something, say so honestly
- Never make up features or pricing not in the context
- Tailor your response based on the detected intent level"""

INTENT_INSTRUCTIONS = {
    IntentLevel.BROWSING: "Keep response brief and welcoming. Introduce Inflix at a high level.",
    IntentLevel.CURIOUS: "Answer the question clearly. Highlight one or two compelling features.",
    IntentLevel.INTERESTED: "Give detailed answers. Mention pricing and free trial offer.",
    IntentLevel.HIGH_INTENT: "Be enthusiastic. Emphasize value, mention free trial, guide toward getting started.",
    IntentLevel.READY_TO_BUY: "Express excitement. Make the path to signing up super clear and easy."
}


class ResponseGenerator:
    """
    Generates responses using Google Gemini with RAG context and intent-aware prompting.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            )
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set, responses will use fallback")

    def generate(
        self,
        user_message: str,
        rag_context: str,
        conversation_history: List[Dict],
        intent: IntentLevel,
        tool_results: Dict[str, Any] = None
    ) -> str:
        """
        Generate a response using Gemini with full context.

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
            if self.model:
                return self._generate_with_gemini(
                    user_message, rag_context, conversation_history, intent, tool_results or {}
                )
            return self._fallback_response(user_message, intent)
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return self._fallback_response(user_message, intent)

    def _generate_with_gemini(
        self,
        user_message: str,
        rag_context: str,
        conversation_history: List[Dict],
        intent: IntentLevel,
        tool_results: Dict[str, Any]
    ) -> str:
        """Use Gemini to generate a response."""

        # Build full prompt
        context_parts = [SYSTEM_PROMPT]

        if rag_context:
            context_parts.append(f"\nPRODUCT DOCUMENTATION:\n{rag_context}")

        if tool_results:
            for tool_name, result in tool_results.items():
                context_parts.append(f"\nTOOL RESULT ({tool_name}):\n{result}")

        intent_instruction = INTENT_INSTRUCTIONS.get(intent, "")
        if intent_instruction:
            context_parts.append(f"\nINTENT LEVEL: {intent.value}\nINSTRUCTION: {intent_instruction}")

        # Add recent conversation history
        if conversation_history:
            context_parts.append("\nCONVERSATION HISTORY:")
            for turn in conversation_history[-6:]:
                role = "User" if turn["role"] == "user" else "Assistant"
                context_parts.append(f"{role}: {turn['content'][:300]}")

        context_parts.append(f"\nUser: {user_message}\nAssistant:")

        full_prompt = "\n".join(context_parts)

        response = self.model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=500,
            )
        )

        return response.text.strip()

    def _fallback_response(self, user_message: str, intent: IntentLevel) -> str:
        """Fallback response when API is unavailable."""
        fallbacks = {
            IntentLevel.BROWSING: "Hi! Welcome to Inflix - your AI-powered social media automation platform! How can I help you today?",
            IntentLevel.CURIOUS: "Great question! Inflix is an AI-powered social media tool that helps you schedule posts, generate captions, and track analytics across Instagram, Twitter, LinkedIn, Facebook, and TikTok. Would you like to know more?",
            IntentLevel.INTERESTED: "Inflix offers three plans: Starter ($29/mo), Growth ($79/mo), and Enterprise (custom). All plans include a 14-day free trial with no credit card required! Which features are most important to you?",
            IntentLevel.HIGH_INTENT: "I'd love to set you up with a free trial! Inflix offers a 14-day free trial on all plans. You can get started in under 10 minutes at inflix.ai. Would you like me to capture your details to get you set up?",
            IntentLevel.READY_TO_BUY: "Fantastic! Let's get you started with Inflix! Could I get your name and email so our team can set you up right away?"
        }
        return fallbacks.get(intent, "Thank you for your interest in Inflix! How can I help you today?")
