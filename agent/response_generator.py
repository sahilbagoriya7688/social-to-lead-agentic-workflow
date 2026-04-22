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
- Be friendly, helpful, and concise
- Focus on Inflix features and benefits
- Encourage users to try the free trial
- If asked about pricing, mention all three plans
- Keep responses under 150 words unless detailed explanation is needed
"""

INTENT_INSTRUCTIONS = {
    IntentLevel.BROWSING: "The user is just exploring. Give a warm welcome and brief product overview.",
    IntentLevel.CURIOUS: "The user has a specific question. Answer it directly using the product documentation provided.",
    IntentLevel.INTERESTED: "The user is interested. Highlight the value proposition and mention the free trial.",
    IntentLevel.HIGH_INTENT: "The user wants to buy. Acknowledge their interest enthusiastically.",
    IntentLevel.READY_TO_BUY: "The user is ready to sign up. Be very enthusiastic and helpful.",
}


class ResponseGenerator:
    """
    Generates responses using Google Gemini with RAG context and intent-aware prompting.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            self.model = genai.GenerativeModel(model_name=model_name)
            logger.info(f"ResponseGenerator initialized with model: {model_name}")
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
        """Generate a response using Gemini with full context."""
        if not self.model:
            return self._fallback_response(user_message, intent)

        try:
            # Build prompt
            context_parts = [SYSTEM_PROMPT]

            if rag_context:
                context_parts.append(f"\nPRODUCT DOCUMENTATION:\n{rag_context}")

            if tool_results:
                for tool_name, result in tool_results.items():
                    context_parts.append(f"\nTOOL RESULT ({tool_name}):\n{result}")

            intent_instruction = INTENT_INSTRUCTIONS.get(intent, "")
            if intent_instruction:
                context_parts.append(f"\nINTENT: {intent_instruction}")

            if conversation_history:
                context_parts.append("\nCONVERSATION HISTORY:")
                for turn in conversation_history[-4:]:
                    role = "User" if turn["role"] == "user" else "Assistant"
                    context_parts.append(f"{role}: {turn['content'][:200]}")

            context_parts.append(f"\nUser: {user_message}\nAssistant:")
            full_prompt = "\n".join(context_parts)

            # Call Gemini API
            response = self.model.generate_content(full_prompt)
            text = response.text.strip()
            if text:
                return text
            return self._fallback_response(user_message, intent)

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_response(user_message, intent)

    def _fallback_response(self, user_message: str, intent: IntentLevel) -> str:
        """Fallback response when API is unavailable."""
        msg = user_message.lower()

        if "instagram" in msg or "tiktok" in msg or "twitter" in msg or "social" in msg:
            return ("Yes! Inflix supports Instagram, TikTok, Twitter/X, LinkedIn, and Facebook. "
                    "You can schedule posts, generate AI captions, and track analytics — all in one place! "
                    "Want to start a free 14-day trial?")

        if "price" in msg or "cost" in msg or "plan" in msg or "much" in msg:
            return ("Inflix has 3 plans:\n"
                    "- **Starter** - $29/month (up to 5 accounts)\n"
                    "- **Growth** - $79/month (up to 15 accounts, most popular)\n"
                    "- **Enterprise** - Custom pricing\n"
                    "All plans include a **14-day free trial**, no credit card required!")

        if "what" in msg or "does" in msg or "how" in msg or "feature" in msg:
            return ("Inflix is an AI-powered social media automation platform! It helps you:\n"
                    "- 📅 Schedule posts across all platforms\n"
                    "- 🤖 Generate AI captions and hashtags\n"
                    "- 📊 Track analytics and competitor performance\n"
                    "- ⏰ Find optimal posting times\n"
                    "Would you like to know more or try it free for 14 days?")

        fallbacks = {
            IntentLevel.BROWSING: "Hi! Welcome to Inflix — your AI-powered social media automation platform! How can I help you today?",
            IntentLevel.CURIOUS: "Great question! Inflix helps you automate social media with AI. It supports Instagram, TikTok, Twitter, LinkedIn and Facebook. Would you like to know more?",
            IntentLevel.INTERESTED: "Inflix offers Starter ($29/mo), Growth ($79/mo), and Enterprise plans. All include a 14-day free trial! What would you like to know more about?",
            IntentLevel.HIGH_INTENT: "Amazing! I'd love to help you get started with Inflix. Could I get your name first?",
            IntentLevel.READY_TO_BUY: "Fantastic! Let's get you set up with Inflix right away. Could I get your name?",
        }
        return fallbacks.get(intent, "Hi! I'm the Inflix AI Assistant. How can I help you today?")
