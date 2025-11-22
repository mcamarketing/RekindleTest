"""
PersonalizerAgent - Message Personalization Specialist

Generates highly personalized email/SMS content using lead data, AI, and
proven copywriting frameworks to maximize engagement and reply rates.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from .base_agent import BaseAgent, MissionContext, AgentResult

logger = logging.getLogger(__name__)


class PersonalizerAgent(BaseAgent):
    """
    Specialized agent for personalized message generation.

    Capabilities:
    - Multi-channel message generation (email, SMS, LinkedIn)
    - AI-powered personalization using lead context
    - A/B test variant creation
    - Subject line optimization
    - Call-to-action generation
    - Tone matching (formal, casual, technical)
    """

    def __init__(self, supabase, redis_client=None, openai_api_key=None):
        super().__init__(
            agent_name="PersonalizerAgent",
            supabase=supabase,
            redis_client=redis_client,
            openai_api_key=openai_api_key
        )

        # Personalization templates
        self.COPYWRITING_FRAMEWORKS = {
            'pas': 'Problem-Agitate-Solution',
            'aida': 'Attention-Interest-Desire-Action',
            'baf': 'Before-After-Bridge',
            'fab': 'Features-Advantages-Benefits',
        }

    async def handle_mission(self, context: MissionContext) -> AgentResult:
        """Execute message personalization mission"""
        logger.info(f"PersonalizerAgent starting mission {context.mission_id}")

        # Get personalization parameters
        lead_ids = context.custom_params.get('lead_ids', [])
        template_type = context.custom_params.get('template_type', 'cold_outreach')
        channel = context.custom_params.get('channel', 'email')
        framework = context.custom_params.get('framework', 'pas')
        generate_variants = context.custom_params.get('generate_variants', False)

        # Step 1: Fetch lead data
        leads = await self._fetch_leads(lead_ids, context.user_id)
        logger.info(f"Personalizing messages for {len(leads)} leads")

        # Step 2: Generate personalized messages
        personalized_messages = []
        for lead in leads:
            message = await self._generate_personalized_message(
                lead=lead,
                template_type=template_type,
                channel=channel,
                framework=framework,
                context=context
            )
            personalized_messages.append(message)

        # Step 3: Generate A/B test variants if requested
        if generate_variants:
            variants = await self._generate_ab_variants(personalized_messages)
            personalized_messages = variants

        # Step 4: Store generated messages
        stored_count = await self._store_messages(personalized_messages, context)

        # Build result
        result_data = {
            'messages_generated': len(personalized_messages),
            'messages_stored': stored_count,
            'channel': channel,
            'framework': framework,
            'template_type': template_type,
            'variants_generated': len(personalized_messages) > len(leads) if generate_variants else False,
        }

        success = stored_count == len(personalized_messages)

        return AgentResult(
            success=success,
            data=result_data,
            message=f"Generated {len(personalized_messages)} personalized {channel} messages using {framework} framework"
        )

    async def _fetch_leads(self, lead_ids: List[str], user_id: str) -> List[Dict[str, Any]]:
        """Fetch lead data for personalization"""
        if not lead_ids:
            return []

        result = self.db.table('leads')\
            .select('*')\
            .eq('user_id', user_id)\
            .in_('id', lead_ids)\
            .execute()

        return result.data if result.data else []

    async def _generate_personalized_message(
        self,
        lead: Dict[str, Any],
        template_type: str,
        channel: str,
        framework: str,
        context: MissionContext
    ) -> Dict[str, Any]:
        """Generate a single personalized message"""

        # Extract personalization variables
        first_name = lead.get('first_name', 'there')
        company = lead.get('company', 'your company')
        industry = lead.get('industry', 'your industry')
        job_title = lead.get('job_title', 'your role')
        pain_points = lead.get('pain_points', [])

        # Build personalization context
        personalization_context = {
            'first_name': first_name,
            'company': company,
            'industry': industry,
            'job_title': job_title,
            'pain_points': pain_points,
            'previous_interaction': lead.get('last_email_topic'),
        }

        # Generate message using LLM if API key available
        if self.openai_api_key:
            generated_content = await self._generate_with_llm(
                personalization_context,
                template_type,
                channel,
                framework
            )
        else:
            # Fallback to template-based generation
            generated_content = self._generate_from_template(
                personalization_context,
                template_type,
                channel,
                framework
            )

        return {
            'lead_id': lead['id'],
            'channel': channel,
            'template_type': template_type,
            'framework': framework,
            'subject_line': generated_content.get('subject_line'),
            'body': generated_content.get('body'),
            'preview_text': generated_content.get('preview_text'),
            'call_to_action': generated_content.get('call_to_action'),
            'personalization_variables': personalization_context,
            'generated_at': datetime.utcnow().isoformat(),
        }

    async def _generate_with_llm(
        self,
        personalization_context: Dict[str, Any],
        template_type: str,
        channel: str,
        framework: str
    ) -> Dict[str, Any]:
        """Generate personalized content using LLM"""
        import openai

        # Build prompt
        prompt = self._build_llm_prompt(
            personalization_context,
            template_type,
            channel,
            framework
        )

        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert B2B copywriter specializing in cold outreach that converts. Write concise, personalized messages that feel human and authentic."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            content = response.choices[0].message.content

            # Parse response (expecting JSON)
            generated = json.loads(content)

            return {
                'subject_line': generated.get('subject_line', ''),
                'body': generated.get('body', ''),
                'preview_text': generated.get('preview_text', ''),
                'call_to_action': generated.get('call_to_action', ''),
            }

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Fallback to template
            return self._generate_from_template(
                personalization_context,
                template_type,
                channel,
                framework
            )

    def _build_llm_prompt(
        self,
        personalization_context: Dict[str, Any],
        template_type: str,
        channel: str,
        framework: str
    ) -> str:
        """Build prompt for LLM message generation"""
        return f"""Generate a personalized {channel} message using the {framework} ({self.COPYWRITING_FRAMEWORKS[framework]}) framework.

Context:
- Recipient: {personalization_context['first_name']} ({personalization_context['job_title']} at {personalization_context['company']})
- Industry: {personalization_context['industry']}
- Pain points: {', '.join(personalization_context['pain_points']) if personalization_context['pain_points'] else 'unknown'}
- Template type: {template_type}

Requirements:
- Keep it under 150 words
- Be conversational and authentic
- Focus on value, not features
- Include a clear, low-friction call-to-action
- Personalize using the context provided

Return JSON format:
{{
  "subject_line": "...",
  "preview_text": "...",
  "body": "...",
  "call_to_action": "..."
}}"""

    def _generate_from_template(
        self,
        personalization_context: Dict[str, Any],
        template_type: str,
        channel: str,
        framework: str
    ) -> Dict[str, Any]:
        """Generate content from predefined templates (fallback)"""
        first_name = personalization_context['first_name']
        company = personalization_context['company']

        # Simple template-based generation
        if framework == 'pas':
            # Problem-Agitate-Solution
            subject_line = f"Quick question about {company}'s growth"
            body = f"""Hi {first_name},

I noticed {company} is scaling in {personalization_context['industry']}.

Most companies at your stage struggle with converting cold leads into meetings. The manual outreach process eats up hours that could be spent closing deals.

We've helped companies like yours automate this completely while keeping it personal. Would you be open to a quick 15-minute call to explore if this could work for you?

Best,
[Your Name]"""
            call_to_action = "Book a 15-minute call"

        elif framework == 'aida':
            # Attention-Interest-Desire-Action
            subject_line = f"{first_name}, saw {company} is hiring"
            body = f"""Hi {first_name},

Congrats on the growth at {company}!

I help {personalization_context['industry']} companies automate their outreach so sales teams can focus on closing instead of prospecting.

We typically see 3x more qualified meetings in the first month. Happy to share how this could work for {company}.

Interested in a quick demo?

Best,
[Your Name]"""
            call_to_action = "See a quick demo"

        else:
            # Default
            subject_line = f"Quick question for {company}"
            body = f"""Hi {first_name},

I help companies in {personalization_context['industry']} streamline their sales outreach.

Would you be open to a brief conversation about how we could help {company}?

Best,
[Your Name]"""
            call_to_action = "Let's chat"

        return {
            'subject_line': subject_line,
            'body': body,
            'preview_text': body.split('\n')[2][:50] + '...',  # First line as preview
            'call_to_action': call_to_action,
        }

    async def _generate_ab_variants(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate A/B test variants for each message"""
        variants = []

        for message in messages:
            # Original (variant A)
            variant_a = {**message, 'variant': 'A'}
            variants.append(variant_a)

            # Variant B: Different subject line
            variant_b = {
                **message,
                'variant': 'B',
                'subject_line': self._generate_alternative_subject(message['subject_line']),
            }
            variants.append(variant_b)

        return variants

    def _generate_alternative_subject(self, original_subject: str) -> str:
        """Generate an alternative subject line"""
        # Simple rule-based alternatives
        if '?' in original_subject:
            return original_subject.replace('?', '')
        elif 'Quick question' in original_subject:
            return original_subject.replace('Quick question', 'Thought')
        else:
            return f"Re: {original_subject}"

    async def _store_messages(
        self,
        messages: List[Dict[str, Any]],
        context: MissionContext
    ) -> int:
        """Store generated messages in database"""
        stored_count = 0

        for message in messages:
            try:
                # Store in personalized_messages table (or equivalent)
                message_data = {
                    'user_id': context.user_id,
                    'mission_id': context.mission_id,
                    'lead_id': message['lead_id'],
                    'channel': message['channel'],
                    'subject_line': message.get('subject_line'),
                    'body': message.get('body'),
                    'call_to_action': message.get('call_to_action'),
                    'variant': message.get('variant', 'A'),
                    'framework': message['framework'],
                    'created_at': datetime.utcnow().isoformat(),
                }

                # For now, store in agent_logs as data
                # In production, would have dedicated table
                self.db.table('agent_logs').insert({
                    'mission_id': context.mission_id,
                    'agent_name': self.agent_name,
                    'event_type': 'custom',
                    'data': {
                        'event': 'message_generated',
                        **message_data
                    }
                }).execute()

                stored_count += 1

            except Exception as e:
                logger.error(f"Failed to store message for lead {message['lead_id']}: {e}")

        return stored_count
