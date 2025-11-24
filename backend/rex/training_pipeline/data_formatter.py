"""
Outcome Data Formatter
Transforms outcome_labels into GPT-4 fine-tuning format (JSONL)

Converts message→outcome chains into training examples:
- Input: Lead context, ICP score, industry, role
- Output: Personalized message that led to positive outcome
- Filters: Only high-quality examples (deals closed, positive replies, meetings booked)
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from supabase import Client

logger = logging.getLogger(__name__)


class OutcomeDataFormatter:
    """Formats outcome labels for GPT-4 fine-tuning"""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def export_training_data(
        self,
        organization_id: Optional[str] = None,
        min_quality_score: float = 0.5,
        include_negative_examples: bool = True,
        limit: int = 10000,
    ) -> List[Dict[str, Any]]:
        """
        Export outcome labels as GPT-4 fine-tuning examples.

        Args:
            organization_id: Filter by organization (None = all orgs)
            min_quality_score: Minimum quality threshold (0.0-1.0)
            include_negative_examples: Include failed messages for learning
            limit: Maximum examples to export

        Returns:
            List of training examples in GPT-4 format
        """
        try:
            # Query training-ready outcomes
            query = (
                self.supabase.table("outcome_labels")
                .select("*")
                .eq("included_in_training", True)
            )

            if organization_id:
                query = query.eq("organization_id", organization_id)

            query = query.order("created_at", desc=True).limit(limit)

            result = query.execute()
            outcomes = result.data

            logger.info(f"Fetched {len(outcomes)} training-ready outcomes")

            # Transform into training examples
            training_examples = []

            for outcome in outcomes:
                # Calculate quality score
                quality_score = self._calculate_quality_score(outcome)

                if quality_score < min_quality_score:
                    continue

                # Skip negative examples if not included
                if not include_negative_examples and outcome.get("training_label") == "negative_example":
                    continue

                # Format as GPT-4 training example
                example = self._format_training_example(outcome, quality_score)

                if example:
                    training_examples.append(example)

            logger.info(
                f"Formatted {len(training_examples)} training examples "
                f"from {len(outcomes)} outcomes"
            )

            return training_examples

        except Exception as e:
            logger.error(f"Failed to export training data: {e}", exc_info=True)
            return []

    def _calculate_quality_score(self, outcome: Dict[str, Any]) -> float:
        """
        Calculate quality score for an outcome (0.0 to 1.0).

        High quality = Deal closed with high value
        Medium quality = Meeting booked or positive reply
        Low quality = Delivered but no engagement
        """
        score = 0.0

        # Base score for delivery
        if outcome.get("delivered"):
            score += 0.1

        # Engagement signals
        if outcome.get("opened"):
            score += 0.1
        if outcome.get("clicked"):
            score += 0.15

        # Reply quality
        if outcome.get("replied"):
            score += 0.2

            sentiment_score = outcome.get("reply_sentiment_score", 0)
            if sentiment_score > 0.5:  # Positive reply
                score += 0.2
            elif sentiment_score < -0.3:  # Negative reply
                score -= 0.1

        # Meeting outcomes
        if outcome.get("meeting_booked"):
            score += 0.3
        if outcome.get("meeting_completed"):
            score += 0.4

        # Revenue outcomes (highest quality)
        if outcome.get("deal_closed"):
            score += 0.5

            # Bonus for high-value deals
            deal_value = float(outcome.get("deal_value", 0))
            if deal_value >= 50000:
                score += 0.2
            elif deal_value >= 20000:
                score += 0.1

        # ICP match bonus
        icp_score = outcome.get("icp_score", 0)
        if icp_score:
            score += icp_score * 0.1  # Up to +0.1 for perfect ICP match

        # Cap at 1.0
        return min(1.0, score)

    def _format_training_example(
        self, outcome: Dict[str, Any], quality_score: float
    ) -> Optional[Dict[str, Any]]:
        """
        Format single outcome as GPT-4 fine-tuning example.

        GPT-4 fine-tuning format:
        {
            "messages": [
                {"role": "system", "content": "..."},
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }
        """
        try:
            # Extract agent decisions
            agent_decisions = outcome.get("agent_decisions", {})
            framework = outcome.get("framework", "unknown")
            tone = outcome.get("tone", "professional")

            # Build context
            lead_context = {
                "industry": outcome.get("lead_industry"),
                "role": outcome.get("lead_role"),
                "seniority": outcome.get("lead_seniority"),
                "company_size": outcome.get("company_size"),
                "icp_score": outcome.get("icp_score"),
            }

            # Build outcome summary
            outcome_summary = self._build_outcome_summary(outcome)

            # System prompt: Define the AI's role
            system_prompt = (
                "You are an expert B2B sales copywriter and personalization specialist. "
                "Your job is to write highly effective, personalized outreach messages that "
                "generate replies, book meetings, and close deals. "
                "You use proven frameworks (PAS, AIDA, BAF, FAB, PASTOR) and adapt tone "
                "based on the lead's industry, role, and seniority. "
                "Every message should be concise, valuable, and focused on the lead's pain points."
            )

            # User prompt: The task with context
            user_prompt = self._build_user_prompt(
                lead_context=lead_context,
                framework=framework,
                tone=tone,
                channel=outcome.get("channel"),
                sequence_step=outcome.get("sequence_step", 1),
            )

            # Assistant response: The winning message
            assistant_response = self._build_assistant_response(
                subject_line=outcome.get("subject_line"),
                message_body=outcome.get("message_body"),
                outcome_summary=outcome_summary,
            )

            # GPT-4 training example
            training_example = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": assistant_response},
                ],
                "metadata": {
                    "outcome_id": outcome.get("id"),
                    "organization_id": outcome.get("organization_id"),
                    "campaign_id": outcome.get("campaign_id"),
                    "quality_score": quality_score,
                    "training_label": outcome.get("training_label"),
                    "training_weight": outcome.get("training_weight"),
                    "deal_value": outcome.get("deal_value"),
                    "created_at": outcome.get("created_at"),
                },
            }

            return training_example

        except Exception as e:
            logger.error(f"Failed to format training example: {e}", exc_info=True)
            return None

    def _build_outcome_summary(self, outcome: Dict[str, Any]) -> str:
        """Build human-readable outcome summary"""
        parts = []

        if outcome.get("deal_closed"):
            deal_value = outcome.get("deal_value", 0)
            parts.append(f"Deal closed: ${deal_value:,.0f}")
        elif outcome.get("meeting_booked"):
            parts.append("Meeting booked")
        elif outcome.get("replied"):
            sentiment = outcome.get("reply_sentiment_label", "neutral")
            parts.append(f"Replied ({sentiment})")
        elif outcome.get("opened"):
            parts.append("Opened")
        elif outcome.get("delivered"):
            parts.append("Delivered")

        return " → ".join(parts) if parts else "No engagement"

    def _build_user_prompt(
        self,
        lead_context: Dict[str, Any],
        framework: str,
        tone: str,
        channel: str,
        sequence_step: int,
    ) -> str:
        """Build user prompt with lead context and requirements"""
        prompt_parts = [
            "Write a personalized outreach message with the following requirements:\n",
        ]

        # Lead context
        prompt_parts.append("\n**Lead Context:**")
        if lead_context.get("industry"):
            prompt_parts.append(f"\n- Industry: {lead_context['industry']}")
        if lead_context.get("role"):
            prompt_parts.append(f"\n- Role: {lead_context['role']}")
        if lead_context.get("seniority"):
            prompt_parts.append(f"\n- Seniority: {lead_context['seniority']}")
        if lead_context.get("company_size"):
            prompt_parts.append(f"\n- Company size: {lead_context['company_size']} employees")
        if lead_context.get("icp_score"):
            prompt_parts.append(f"\n- ICP match: {lead_context['icp_score']:.0%}")

        # Requirements
        prompt_parts.append("\n\n**Requirements:**")
        prompt_parts.append(f"\n- Framework: {framework}")
        prompt_parts.append(f"\n- Tone: {tone}")
        prompt_parts.append(f"\n- Channel: {channel}")
        prompt_parts.append(f"\n- Sequence step: {sequence_step}")

        # Instructions
        prompt_parts.append(
            "\n\n**Instructions:**"
            "\n- Personalize based on their industry, role, and pain points"
            "\n- Use the specified framework and tone"
            "\n- Keep it concise (150-200 words for email, 50-75 for LinkedIn)"
            "\n- Focus on value, not features"
            "\n- Include a clear call-to-action"
            "\n- Avoid hype, buzzwords, and salesy language"
        )

        return "".join(prompt_parts)

    def _build_assistant_response(
        self,
        subject_line: Optional[str],
        message_body: str,
        outcome_summary: str,
    ) -> str:
        """Build assistant response with message and outcome"""
        response_parts = []

        if subject_line:
            response_parts.append(f"**Subject:** {subject_line}\n\n")

        response_parts.append(f"**Message:**\n{message_body}\n\n")

        response_parts.append(f"**Outcome:** {outcome_summary}")

        return "".join(response_parts)

    async def export_to_jsonl(
        self,
        output_path: str,
        organization_id: Optional[str] = None,
        min_quality_score: float = 0.5,
        include_negative_examples: bool = True,
    ) -> int:
        """
        Export training examples to JSONL file (GPT-4 fine-tuning format).

        Args:
            output_path: Path to output JSONL file
            organization_id: Filter by organization
            min_quality_score: Minimum quality threshold
            include_negative_examples: Include failed messages

        Returns:
            Number of examples exported
        """
        try:
            # Get training examples
            examples = await self.export_training_data(
                organization_id=organization_id,
                min_quality_score=min_quality_score,
                include_negative_examples=include_negative_examples,
            )

            # Write to JSONL file
            with open(output_path, "w", encoding="utf-8") as f:
                for example in examples:
                    # Remove metadata (not part of training format)
                    training_example = {"messages": example["messages"]}
                    f.write(json.dumps(training_example) + "\n")

            logger.info(f"Exported {len(examples)} examples to {output_path}")

            return len(examples)

        except Exception as e:
            logger.error(f"Failed to export to JSONL: {e}", exc_info=True)
            return 0

    async def get_training_stats(
        self, organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get statistics about available training data"""
        try:
            query = (
                self.supabase.table("outcome_labels")
                .select("training_label, deal_closed, meeting_booked, replied")
                .eq("included_in_training", True)
            )

            if organization_id:
                query = query.eq("organization_id", organization_id)

            result = query.execute()
            outcomes = result.data

            stats = {
                "total_examples": len(outcomes),
                "positive_examples": len(
                    [o for o in outcomes if o.get("training_label") == "positive_example"]
                ),
                "negative_examples": len(
                    [o for o in outcomes if o.get("training_label") == "negative_example"]
                ),
                "neutral_examples": len(
                    [o for o in outcomes if o.get("training_label") == "neutral"]
                ),
                "deals_closed": len([o for o in outcomes if o.get("deal_closed")]),
                "meetings_booked": len([o for o in outcomes if o.get("meeting_booked")]),
                "replies": len([o for o in outcomes if o.get("replied")]),
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get training stats: {e}", exc_info=True)
            return {}


# Factory function
def create_outcome_data_formatter(supabase: Client) -> OutcomeDataFormatter:
    """Create OutcomeDataFormatter instance"""
    return OutcomeDataFormatter(supabase)
