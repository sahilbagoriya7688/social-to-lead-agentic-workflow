"""
Intent Detector - Classifies user messages into intent levels
to determine how to route the conversation.
"""

import os
import logging
from enum import Enum
from typing import List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class IntentLevel(Enum):
    """Intent levels from lowest to highest purchase intent."""
    BROWSING = "BROWSING"
    CURIOUS = "CURIOUS"
    INTERESTED = "INTERESTED"
    HIGH_INTENT = "HIGH_INTENT"
    READY_TO_BUY = "READY_TO_BUY"


INTENT_SYSTEM_PROMPT = """You are an intent classifier for Inflix, an AI-powered social media automation SaaS.

Classify the user's message into ONE of these intent levels:

1. BROWSING - User is just exploring, no specific interest or questions
   Examples: "hi", "what's this?", "tell me about AI tools"

2. CURIOUS - User is asking general questions about the product
   Examples: "what does Inflix do?", "how does AI automation work?"

3. INTERESTED - User is genuinely interested, asking about features or pricing
   Examples: "what features do you have?", "how much does it cost?", "do you integrate with Instagram?"

4. HIGH_INTENT - User is actively evaluating, asking about trials, demos, or comparison
   Examples: "can I try it free?", "I want to see a demo", "how is this better than Hootsuite?"

5. READY_TO_BUY - User is ready to sign up or purchase
   Examples: "I want to sign up", "how do I get started?", "I'm ready to buy", "let's do this"

Also consider CONVERSATION HISTORY to upgrade intent levels (e.g., if someone was INTERESTED and now asks a follow-up, they might be HIGH_INTENT).

Respond with ONLY the intent level name (e.g., "CURIOUS"), nothing else."""


class IntentDetector:
    """
    Detects user intent using an LLM-based classifier.
    Falls back to keyword-based detection if LLM is unavailable.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        
        # Keyword-based fallback patterns
        self.intent_keywords = {
            IntentLevel.READY_TO_BUY: [
                "sign up", "buy", "purchase", "subscribe", "get started",
                "ready to", "let's do", "i want to start", "take my money",
                "how do i pay", "billing", "checkout"
            ],
            IntentLevel.HIGH_INTENT: [
                "demo", "trial", "free trial", "test it", "try it",
                "compare", "vs", "better than", "competitor", "switch from",
                "onboarding", "setup", "migrate"
            ],
            IntentLevel.INTERESTED: [
                "price", "cost", "pricing", "plan", "feature", "integration",
                "does it", "can it", "support", "work with", "connect to",
                "how many", "limit"
            ],
            IntentLevel.CURIOUS: [
                "what is", "what does", "how does", "explain", "tell me about",
                "why", "who is", "what kind"
            ]
        }
    
    def detect(self, message: str, conversation_history: List[dict] = None) -> IntentLevel:
        """
        Detect the intent level of a user message.
        
        Args:
            message: The user's message
            conversation_history: Previous conversation turns
            
        Returns:
            IntentLevel enum value
        """
        try:
            return self._detect_with_llm(message, conversation_history or [])
        except Exception as e:
            logger.warning(f"LLM intent detection failed: {e}. Falling back to keyword matching.")
            return self._detect_with_keywords(message)
    
    def _detect_with_llm(self, message: str, conversation_history: List[dict]) -> IntentLevel:
        """Use GPT to classify intent."""
        # Build context from recent history
        history_context = ""
        if conversation_history:
            recent = conversation_history[-6:]  # Last 3 exchanges
            history_context = "\nRecent conversation:\n"
            for turn in recent:
                role = "User" if turn["role"] == "user" else "Assistant"
                history_context += f"{role}: {turn['content'][:200]}\n"
        
        user_prompt = f"{history_context}\nCurrent message: {message}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            max_tokens=20
        )
        
        intent_str = response.choices[0].message.content.strip().upper()
        
        # Map to IntentLevel
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
        
        # Check from highest to lowest intent
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
