"""
Sentiment Analyzer - Reply Classification
Part of: Flywheel Architecture - Outcome Labeling System

Analyzes lead replies to classify:
- Sentiment (positive, neutral, negative)
- Interest signals (high, medium, low)
- Objection types (price, timing, authority, competitor, not_interested)

Uses OpenAI GPT-4 for nuanced understanding of B2B sales replies.
"""

import logging
import os
from typing import Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
from enum import Enum
import json

logger = logging.getLogger(__name__)


class SentimentLabel(str, Enum):
    """Sentiment classification"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class InterestLevel(str, Enum):
    """Interest signal strength"""
    HIGH = "high"  # "Let's schedule a call", "Tell me more", "Interested"
    MEDIUM = "medium"  # "Maybe", "Not now but keep me posted"
    LOW = "low"  # Minimal engagement
    NONE = "none"  # No interest signal


class ObjectionType(str, Enum):
    """Common objections in B2B sales"""
    PRICE = "price"  # "Too expensive", "What's the cost"
    TIMING = "timing"  # "Not right now", "Maybe next quarter"
    AUTHORITY = "authority"  # "I need to check with my boss"
    COMPETITOR = "competitor"  # "We're using X already"
    NOT_INTERESTED = "not_interested"  # "Not interested", "Remove me"
    NO_NEED = "no_need"  # "We don't need this"
    NONE = "none"  # No objection detected


class SentimentAnalyzer:
    """Analyzes lead replies using GPT-4"""

    def __init__(self, openai_api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"))

    async def analyze_reply(
        self,
        reply_text: str,
        original_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a lead's reply for sentiment, interest, and objections.

        Args:
            reply_text: The lead's reply text
            original_message: The message we sent (provides context)
            context: Additional context (industry, role, etc.)

        Returns:
            {
                "sentiment_score": float (-1.0 to 1.0),
                "sentiment_label": "positive" | "neutral" | "negative",
                "interest_signal": bool,
                "interest_level": "high" | "medium" | "low" | "none",
                "objection_detected": bool,
                "objection_type": "price" | "timing" | ... | "none",
                "reasoning": str (explanation of classification)
            }
        """
        try:
            # Build analysis prompt
            prompt = self._build_analysis_prompt(reply_text, original_message, context)

            # Call GPT-4 for analysis
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert B2B sales analyst. "
                            "Analyze lead replies to classify sentiment, interest signals, and objections. "
                            "Respond ONLY with valid JSON."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for consistent classification
                response_format={"type": "json_object"}
            )

            # Parse GPT-4 response
            analysis = json.loads(response.choices[0].message.content)

            # Validate and normalize
            result = {
                "sentiment_score": float(analysis.get("sentiment_score", 0.0)),
                "sentiment_label": analysis.get("sentiment_label", SentimentLabel.NEUTRAL),
                "interest_signal": analysis.get("interest_signal", False),
                "interest_level": analysis.get("interest_level", InterestLevel.NONE),
                "objection_detected": analysis.get("objection_detected", False),
                "objection_type": analysis.get("objection_type", ObjectionType.NONE),
                "reasoning": analysis.get("reasoning", ""),
            }

            # Ensure sentiment_score is in range
            result["sentiment_score"] = max(-1.0, min(1.0, result["sentiment_score"]))

            logger.info(
                f"Analyzed reply: sentiment={result['sentiment_label']}, "
                f"interest={result['interest_level']}, "
                f"objection={result['objection_type']}"
            )

            return result

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}", exc_info=True)
            # Return neutral default if analysis fails
            return {
                "sentiment_score": 0.0,
                "sentiment_label": SentimentLabel.NEUTRAL,
                "interest_signal": False,
                "interest_level": InterestLevel.NONE,
                "objection_detected": False,
                "objection_type": ObjectionType.NONE,
                "reasoning": f"Analysis failed: {str(e)}",
            }

    def _build_analysis_prompt(
        self,
        reply_text: str,
        original_message: Optional[str],
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Build the analysis prompt for GPT-4"""

        prompt_parts = [
            "Analyze this B2B sales reply and classify:\n",
            "1. Sentiment (score from -1.0 to 1.0, label: positive/neutral/negative)",
            "2. Interest signal (is the lead interested? true/false)",
            "3. Interest level (high/medium/low/none)",
            "4. Objection type (price/timing/authority/competitor/not_interested/no_need/none)\n",
        ]

        if original_message:
            prompt_parts.append(f"\n**Our Message:**\n{original_message}\n")

        prompt_parts.append(f"\n**Lead's Reply:**\n{reply_text}\n")

        if context:
            prompt_parts.append(f"\n**Context:**\n")
            if context.get("industry"):
                prompt_parts.append(f"- Industry: {context['industry']}\n")
            if context.get("role"):
                prompt_parts.append(f"- Role: {context['role']}\n")

        prompt_parts.append(
            "\n**Classification Guidelines:**\n"
            "- **Positive sentiment (0.5 to 1.0)**: Enthusiastic, interested, asking questions, wants to learn more\n"
            "- **Neutral sentiment (-0.2 to 0.5)**: Polite acknowledgment, minor questions, non-committal\n"
            "- **Negative sentiment (-1.0 to -0.2)**: Rejection, annoyance, unsubscribe request\n\n"
            "- **High interest**: \"Let's schedule a call\", \"Tell me more\", \"I'm interested\", asks specific questions\n"
            "- **Medium interest**: \"Maybe\", \"Not now but keep me posted\", asks vague questions\n"
            "- **Low interest**: Minimal engagement, very short reply\n\n"
            "- **Price objection**: Mentions cost, budget, expensive\n"
            "- **Timing objection**: \"Not right now\", \"Maybe next quarter\", \"Too busy\"\n"
            "- **Authority objection**: \"I need to check with my boss/team\"\n"
            "- **Competitor objection**: \"We're using X\", \"Already have a solution\"\n"
            "- **Not interested**: Direct rejection, unsubscribe, \"not interested\"\n"
            "- **No need**: \"We don't need this\", \"Not relevant to us\"\n"
        )

        prompt_parts.append(
            "\nRespond with JSON ONLY:\n"
            "{\n"
            '  "sentiment_score": -1.0 to 1.0,\n'
            '  "sentiment_label": "positive" | "neutral" | "negative",\n'
            '  "interest_signal": true | false,\n'
            '  "interest_level": "high" | "medium" | "low" | "none",\n'
            '  "objection_detected": true | false,\n'
            '  "objection_type": "price" | "timing" | "authority" | "competitor" | "not_interested" | "no_need" | "none",\n'
            '  "reasoning": "Brief explanation of classification (1-2 sentences)"\n'
            "}"
        )

        return "".join(prompt_parts)

    async def analyze_batch(
        self,
        replies: list[Dict[str, Any]],
    ) -> list[Dict[str, Any]]:
        """
        Analyze multiple replies in batch (for processing historical data).

        Args:
            replies: List of dicts with keys: reply_text, original_message (optional), context (optional)

        Returns:
            List of analysis results matching input order
        """
        import asyncio

        tasks = [
            self.analyze_reply(
                reply_text=reply["reply_text"],
                original_message=reply.get("original_message"),
                context=reply.get("context"),
            )
            for reply in replies
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to neutral results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch analysis error: {result}")
                processed_results.append({
                    "sentiment_score": 0.0,
                    "sentiment_label": SentimentLabel.NEUTRAL,
                    "interest_signal": False,
                    "interest_level": InterestLevel.NONE,
                    "objection_detected": False,
                    "objection_type": ObjectionType.NONE,
                    "reasoning": f"Error: {str(result)}",
                })
            else:
                processed_results.append(result)

        return processed_results

    def quick_classify(self, reply_text: str) -> Tuple[SentimentLabel, bool]:
        """
        Quick rule-based classification for simple cases (fallback if GPT-4 fails).

        Returns:
            (sentiment_label, interest_signal)
        """
        reply_lower = reply_text.lower()

        # Strong positive signals
        positive_keywords = [
            "interested", "yes", "let's schedule", "tell me more", "sounds good",
            "book a call", "when can we", "i'd like to", "let's talk"
        ]

        # Strong negative signals
        negative_keywords = [
            "not interested", "unsubscribe", "remove me", "stop", "no thanks",
            "don't contact", "leave me alone"
        ]

        # Interest signals
        interest_keywords = [
            "interested", "more info", "tell me", "schedule", "call", "demo",
            "pricing", "how does", "what is", "can you"
        ]

        # Check for strong signals
        if any(keyword in reply_lower for keyword in positive_keywords):
            return SentimentLabel.POSITIVE, True

        if any(keyword in reply_lower for keyword in negative_keywords):
            return SentimentLabel.NEGATIVE, False

        # Check for interest
        has_interest = any(keyword in reply_lower for keyword in interest_keywords)

        # Default to neutral
        return SentimentLabel.NEUTRAL, has_interest


# Factory function
def create_sentiment_analyzer(openai_api_key: Optional[str] = None) -> SentimentAnalyzer:
    """Create SentimentAnalyzer instance"""
    return SentimentAnalyzer(openai_api_key)
