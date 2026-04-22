"""
Intent Detector - Classifies user intent using Google Gemini AI.
Detects purchase intent levels from conversational messages.
"""

import os
import logging
from enum import Enum
from typing import List, Dict
from google import genai

logger = logging.getLogger(__name__)


class IntentLevel(Enum):
    BROWSING = "BROWSING"
    CURIOUS = "CURIOUS"
    INTERESTED = "INTERESTED"
    HIGH_INTENT = "HIGH_INTENT"
    READY_TO_BUY = "READY_TO_BUY"


INTENT_KEYWORDS = {
    IntentLevel.READY_TO_BUY: [
        "sign up", "signup", "register", "buy now", "purchase", "subscribe",
        "ready to buy", "ready to sign", "i want to buy", "take my money",
        "get started", "start now", "ready", "let's go", "yes please"
    ],
    IntentLevel.HIGH_INTENT: [
        "i want to try", "want to try", "interested in buying", "how do i sign up",
        "where do i sign up", "i'm in", "book a demo", "schedule demo",
        "free trial", "try it", "want it", "need this", "this is great",
        "i want this", "sign me up", "count me in"
    ],
    IntentLevel.INTERESTED: [
        "how much", "price", "pricing", "cost", "plans", "subscription",
        "compare", "vs", "versus", "better than", "features", "what can",
        "does it", "can it", "will it", "is it", "monthly", "annually",
        "discount", "offer", "deal", "cheap", "affordable", "expensive"
    ],
    IntentLevel.CURIOUS: [
        "what is", "how does", "tell me", "explain", "works with", "support",
        "instagram", "twitter", "facebook", "linkedin", "tiktok", "youtube",
        "analytics", "schedule", "post", "caption", "ai", "automation",
        "whatsapp", "platform", "integration", "api", "connect"
    ],
}


class IntentDetector:
    """Detects user intent using Gemini AI with keyword fallback."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
                logger.info(f"IntentDetector initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to init Gemini client: {e}")
                self.client = None
                self.model = None
        else:
            self.client = None
            self.model = None
            logger.warning("GEMINI_API_KEY not set, using keyword fallback")

    def detect(self, user_message: str, conversation_history: List[Dict] = None) -> IntentLevel:
        """Detect the intent level of a user message."""
        if self.client:
            try:
                return self._detect_with_gemini(user_message, conversation_history)
            except Exception as e:
                logger.error(f"Gemini intent detection failed: {e}. Using keyword fallback.")
        return self._detect_with_keywords(user_message)

    def _detect_with_gemini(self, user_message: str, conversation_history: List[Dict] = None) -> IntentLevel:
        """Use Gemini to classify intent."""
        prompt = f"""Classify the purchase intent of this message for a SaaS product.

Intent levels:
- READY_TO_BUY: User wants to sign up or buy right now
- HIGH_INTENT: User wants to try or is very interested in starting
- INTERESTED: User asking about pricing, features, or comparisons
- CURIOUS: User asking general questions about the product
- BROWSING: Just exploring or off-topic

Message: "{user_message}"

Reply with ONLY one of: READY_TO_BUY, HIGH_INTENT, INTERESTED, CURIOUS, BROWSING"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        result = response.text.strip().upper()
        for level in IntentLevel:
            if level.value in result:
                return level
        return IntentLevel.BROWSING

    def _detect_with_keywords(self, user_message: str) -> IntentLevel:
        """Fallback keyword-based intent detection."""
        msg = user_message.lower()
        for intent_level in [
            IntentLevel.READY_TO_BUY,
            IntentLevel.HIGH_INTENT,
            IntentLevel.INTERESTED,
            IntentLevel.CURIOUS,
        ]:
            keywords = INTENT_KEYWORDS.get(intent_level, [])
            if any(kw in msg for kw in keywords):
                return intent_level
        return IntentLevel.BROWSING
