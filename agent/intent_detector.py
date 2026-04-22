"""
Intent Detector - Classifies user messages into intent levels
to determine how to route the conversation.
Uses Google Gemini API (free tier).
"""

import os
import logging
from enum import Enum
from typing import List

# ✅ FIXED: Use new google-genai SDK instead of deprecated google.generativeai
from google import genai

logger = logging.getLogger(__name__)


class IntentLevel(Enum):
    """Intent levels from lowest to highest purchase intent."""
    BROWSING = "BROWSING"
    CURIOUS = "CURIOUS"
    INTERESTED = "INTERESTED"
    HIGH_INTENT = "HIGH_INTENT"
    READY_TO_BUY = "READY_TO_BUY"


INTENT_SYSTEM_PROMPT = """You are an intent classifier for Inflix, an AI-powered social media automation SaaS.

Classify the user message into ONE of these intent levels:

1. BROWSING - Just exploring, no specific interest. E.g. "hi", "hello"
2. CURIOUS - Asking general questions. E.g. "what does Inflix do?"
3. INTERESTED - Asking about features or pricing. E.g. "how much does it cost?", "what features do you have?"
4. HIGH_INTENT - Actively evaluating, wants demo/trial. E.g. "can I try it?", "I want to see a demo"
5. READY_TO_BUY - Ready to sign up. E.g. "I want to sign up", "let's get started", "I'm ready to buy"

Respond with ONLY the intent level name (e.g., "CURIOUS"), nothing else."""


class IntentDetector:
    """
    Detects user intent using Google Gemini API.
    Falls back to keyword-based detection if API is unavailable.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            # ✅ FIXED: New SDK initialization
            self.client = genai.Client(api_key=api_key)
            # ✅ FIXED: Updated model name
            self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            logger.info(f"IntentDetector initialized with model: {self.model_name}")
        else:
            self.client = None
            self.model_name = None
            logger.warning("GEMINI_API_KEY not set, using keyword fallback")

        # Keyword-based fallback
        self.intent_keywords = {
            IntentLevel.READY_TO_BUY: [
                "sign up", "buy", "purchase", "subscribe", "get started",
                "ready to", "let's do", "i want to start", "how do i pay",
                "billing", "checkout", "take my money"
            ],
            IntentLevel.HIGH_INTENT: [
                "demo", "trial", "free trial", "test it", "try it",
                "compare", "vs", "better than", "competitor", "switch from",
                "onboarding", "setup", "migrate", "can i try"
            ],
            IntentLevel.INTERESTED: [
                "price", "cost", "pricing", "plan", "feature", "integration",
                "does it", "can it", "support", "work with", "connect",
                "how many", "limit", "how much"
            ],
            IntentLevel.CURIOUS: [
                "what is", "what does", "how does", "explain", "tell me",
                "why", "who is", "what kind", "what can"
            ]
        }

    def detect(self, message: str, conversation_history: List[dict] = None) -> IntentLevel:
        """Detect the intent level of a user message."""
        try:
            if self.client:
                return self._detect_with_gemini(message, conversation_history or [])
            return self._detect_with_keywords(message)
        except Exception as e:
            logger.warning(f"Gemini intent detection failed: {e}. Using keyword fallback.")
            return self._detect_with_keywords(message)

    def _detect_with_gemini(self, message: str, conversation_history: List[dict]) -> IntentLevel:
        """Use Gemini to classify intent."""
        history_context = ""
        if conversation_history:
            recent = conversation_history[-4:]
            history_context = "Recent conversation:\n"
            for turn in recent:
                role = "User" if turn["role"] == "user" else "Assistant"
                history_context += f"{role}: {turn['content'][:150]}\n"

        prompt = f"{INTENT_SYSTEM_PROMPT}\n\n{history_context}\nCurrent message: {message}"

        # ✅ FIXED: New SDK call syntax
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        intent_str = response.text.strip().upper()

        intent_map = {
            "BROWSING": IntentLevel.BROWSING,
            "CURIOUS": IntentLevel.CURIOUS,
            "INTERESTED": IntentLevel.INTERESTED,
            "HIGH_INTENT": IntentLevel.HIGH_INTENT,
            "READY_TO_BUY": IntentLevel.READY_TO_BUY
        }
        return intent_map.get(intent_str, IntentLevel.CURIOUS)

    def _detect_with_keywords(self, message: str) -> IntentLevel:
        """Keyword-based fallback intent detection."""
        message_lower = message.lower()
        for intent_level in [
            IntentLevel.READY_TO_BUY,
            IntentLevel.HIGH_INTENT,
            IntentLevel.INTERESTED,
            IntentLevel.CURIOUS
        ]:
            keywords = self.intent_keywords.get(intent_level, [])
            if any(keyword in message_lower for keyword in keywords):
                return intent_level
        return IntentLevel.BROWSING

    def get_intent_description(self, intent: IntentLevel) -> str:
        """Get a human-readable description of an intent level."""
        descriptions = {
            IntentLevel.BROWSING: "Just browsing, no specific interest",
            IntentLevel.CURIOUS: "Asking general questions",
            IntentLevel.INTERESTED: "Genuinely interested in features/pricing",
            IntentLevel.HIGH_INTENT: "Actively evaluating the product",
            IntentLevel.READY_TO_BUY: "Ready to sign up or purchase"
        }
        return descriptions.get(intent, "Unknown intent")
