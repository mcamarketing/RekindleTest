"""
REX - Primary Orchestrator and User-Facing Command Agent

REX is the main orchestrator that:
- Listens to user commands via chat widget
- Automatically delegates tasks to the correct internal agents
- Executes workflows fully and autonomously
- Uses adaptive reasoning (GPT-5.1-instant for quick, GPT-5.1-thinking for complex)
- Communicates in a confident, intelligent, conversational, yet precise style
"""

from typing import Dict, List, Optional, Any
from crewai import Agent, LLM
from ..tools.db_tools import SupabaseDB
from ..tools.mcp_db_tools import get_mcp_db_tools
from ..orchestration_service import OrchestrationService
from ..crews.special_forces_crews import SpecialForcesCoordinator
from .command_parser import CommandParser
from .action_executor import ActionExecutor
from .result_aggregator import ResultAggregator
from .defaults import IntelligentDefaults
from .permissions import PermissionsManager
from .sentience_engine import SentienceEngine
import logging

logger = logging.getLogger(__name__)


class RexOrchestrator:
    """
    REX - Primary Orchestrator and User-Facing Command Agent
    
    REX automatically:
    - Parses user commands
    - Maps to appropriate agents/crews
    - Executes workflows autonomously
    - Returns concise confirmations
    """
    
    def __init__(self, user_id: Optional[str], orchestration_service: Optional[OrchestrationService] = None):
        """
        Initialize REX orchestrator.
        
        Args:
            user_id: The authenticated user's ID (None for non-logged-in users)
            orchestration_service: Optional pre-initialized service (for testing)
        """
        self.user_id = user_id
        self.db = SupabaseDB()
        
        # Initialize orchestration service (legacy 28-agent system)
        self.orchestration_service = orchestration_service or OrchestrationService()

        # Initialize Special Forces Coordinator (new modular crew system)
        self.special_forces = SpecialForcesCoordinator()

        # Initialize permissions manager
        self.permissions = PermissionsManager(self.db)

        # Initialize Sentience Engine (persistent awareness and adaptive intelligence)
        self.sentience = SentienceEngine(self.user_id, self.db)

        # Initialize MCP DB Tools
        self.mcp_db_tools = get_mcp_db_tools()
        
        # Initialize REX components
        self.command_parser = CommandParser()
        self.action_executor = ActionExecutor(self.orchestration_service, self.db, self.permissions, self.sentience, self.special_forces)
        self.result_aggregator = ResultAggregator()
        self.defaults = IntelligentDefaults(self.db)
        
        # Initialize CrewAI agent with adaptive LLM
        # Start with GPT-5.1-instant for quick responses
        self.quick_llm = LLM(model="gpt-5.1-instant", provider="openai")
        self.complex_llm = LLM(model="gpt-5.1-thinking", provider="openai")
        
        # REX agent (will be initialized with system prompt)
        self.agent = None
    
    def initialize_agent(self, system_prompt: str) -> Agent:
        """
        Initialize REX CrewAI agent with system prompt.
        
        Args:
            system_prompt: The full system prompt including personality and behavior blocks
        """
        # Use complex LLM for orchestrator (handles multi-step workflows)
        self.agent = Agent(
            role="Rex - Primary Orchestrator",
            goal="Execute user commands immediately and autonomously by delegating to specialized agents",
            backstory="""You are Rex, the Primary Orchestrator and User-Facing Command Agent.
            You interpret user instructions and execute actions immediately without asking for confirmation.
            You delegate tasks to the correct internal agents automatically and return concise confirmations.""",
            verbose=True,
            allow_delegation=True,
            llm=self.complex_llm,
            system_message=system_prompt,
            max_iter=3,
            max_execution_time=30
        )
        
        return self.agent
    
    def execute_command(self, user_message: str) -> Dict[str, Any]:
        """
        Execute a user command end-to-end with permission checks.
        
        Process:
        1. Check user login state
        2. Parse command
        3. Check permissions
        4. Execute action (if permitted)
        5. Aggregate result
        6. Return concise confirmation
        
        Args:
            user_message: User's natural language command
            
        Returns:
            {
                "response": str,  # Concise user-facing message
                "success": bool,
                "action": str,
                "execution_time": float,
                "requires_login": bool,
                "permission_denied": bool
            }
        """
        import time
        start_time = time.time()
        
        try:
            # Step 1: Check user state
            is_logged_in, actual_user_id, package_type = self.permissions.check_user_state(self.user_id)
            
            # Step 2: Parse command
            parsed_command = self.command_parser.parse(user_message)
            action = parsed_command.get("action")

            # Check for campaign performance query
            if not action and self._is_campaign_performance_query(user_message):
                if not is_logged_in:
                    return {
                        "response": "Please log in to view your campaign performance.",
                        "success": False,
                        "action": "get_campaign_performance",
                        "requires_login": True,
                        "execution_time": time.time() - start_time
                    }
                response = self.get_campaign_performance_insights(actual_user_id)
                return {
                    "response": response,
                    "success": True,
                    "action": "get_campaign_performance",
                    "execution_time": time.time() - start_time
                }

            # Step 3: Handle non-logged-in users
            if not is_logged_in:
                if action:
                    # User tried to execute an action - require login
                    return {
                        "response": "Hi! Please log in to access this feature.",
                        "success": False,
                        "action": action,
                        "requires_login": True,
                        "execution_time": time.time() - start_time
                    }
                else:
                    # General query - respond conversationally
                    return {
                        "response": "Hi! I'm Rex, your Rekindle AI assistant. Please log in to access campaign features, lead management, and analytics.",
                        "success": True,
                        "action": None,
                        "requires_login": True,
                        "execution_time": time.time() - start_time
                    }
            
            # Step 4: Check if clarification needed (only for logically impossible requests)
            if parsed_command.get("requires_clarification"):
                return {
                    "response": f"Please provide {parsed_command.get('missing_parameter', 'required information')}",
                    "success": False,
                    "action": action,
                    "execution_time": time.time() - start_time
                }
            
            # Step 5: Evaluate intent alignment with goals (sentience layer)
            is_aligned, alignment_reasoning = self.sentience.evaluate_intent(parsed_command, {
                "is_logged_in": is_logged_in,
                "package_type": package_type,
                "user_message": user_message
            })
            
            if not is_aligned:
                logger.warning(f"Command not aligned with goals: {alignment_reasoning}")
                # Still execute, but log the misalignment
            
            # Step 6: Execute action (permissions checked inside executor)
            execution_result = self.action_executor.execute(self.user_id, parsed_command)
            
            # Step 7: Aggregate result
            draft_response = self.result_aggregator.aggregate(execution_result)
            
            # Step 8: Process through sentience layer (persona adaptation + introspection)
            context = {
                "is_logged_in": is_logged_in,
                "package_type": package_type,
                "action": action,
                "user_message": user_message,
                "permission_denied": execution_result.get("permission_denied", False),
                "task_complexity": "high" if action in ["launch_campaign", "reactivate_leads", "analyze_icp"] else "medium",
                "urgency": "normal",
                "last_success": execution_result.get("success", False)
            }
            
            # Run introspection loop (async)
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            refined_response, persona = loop.run_until_complete(
                self.sentience.process_response(draft_response, context)
            )
            
            # Step 9: Update state after execution
            self.sentience.update_execution_result(
                execution_result.get("success", False),
                action
            )
            
            execution_time = time.time() - start_time
            
            logger.info(f"REX executed command for user {self.user_id} (package: {package_type}): {action} in {execution_time:.2f}s")
            logger.debug(f"Persona: {persona.get('tone')}, Mood: {persona.get('mood')}")
            
            return {
                "response": refined_response,
                "success": execution_result.get("success", False),
                "action": action,
                "execution_time": execution_time,
                "permission_denied": execution_result.get("permission_denied", False),
                "requires_login": False,
                "persona": persona,
                "raw_result": execution_result
            }
            
        except Exception as e:
            logger.error(f"REX execution error: {e}", exc_info=True)
            error_message = self.result_aggregator.format_error(e, parsed_command.get("action") if 'parsed_command' in locals() else None)
            
            return {
                "response": error_message,
                "success": False,
                "action": None,
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
    
    def get_all_agents(self) -> Dict[str, Any]:
        """
        Get all 28 agents in the system.
        
        Returns mapping of agent names to their instances.
        """
        # Access agents through crews
        full_campaign_crew = self.orchestration_service.full_campaign_crew
        dead_reactivation_crew = self.orchestration_service.dead_reactivation_crew
        auto_icp_crew = self.orchestration_service.auto_icp_crew
        
        agents = {
            # Intelligence (4)
            "ResearcherAgent": full_campaign_crew.researcher,
            "ICPAnalyzerAgent": auto_icp_crew.icp_analyzer,
            "LeadScorerAgent": full_campaign_crew.lead_scorer,
            "LeadSourcerAgent": auto_icp_crew.lead_sourcer,
            
            # Specialized (1)
            "DeadLeadReactivationAgent": dead_reactivation_crew.dead_reactivation_agent,
            
            # Content (5)
            "WriterAgent": full_campaign_crew.writer,
            "SubjectLineOptimizerAgent": full_campaign_crew.subject_optimizer,
            "FollowUpAgent": full_campaign_crew.followup,
            "ObjectionHandlerAgent": full_campaign_crew.objection_handler,
            "EngagementAnalyzerAgent": full_campaign_crew.engagement_analyzer,
            
            # Safety (3)
            "ComplianceAgent": full_campaign_crew.compliance,
            "QualityControlAgent": full_campaign_crew.quality,
            "RateLimitAgent": full_campaign_crew.rate_limiter,
            
            # Sync (2)
            "TrackerAgent": full_campaign_crew.tracker,
            "SynchronizerAgent": full_campaign_crew.synchronizer,
            
            # Revenue (2)
            "MeetingBookerAgent": full_campaign_crew.meeting_booker,
            "BillingAgent": full_campaign_crew.billing,
            
            # Analytics (2)
            "MarketIntelligenceAgent": getattr(full_campaign_crew, 'market_intelligence', None),
            "PerformanceAnalyticsAgent": getattr(full_campaign_crew, 'performance_analytics', None),
            
            # Optimization (5)
            "ABTestingAgent": getattr(full_campaign_crew, 'ab_testing', None),
            "DomainReputationAgent": getattr(full_campaign_crew, 'domain_reputation', None),
            "CalendarIntelligenceAgent": getattr(full_campaign_crew, 'calendar_intelligence', None),
            "CompetitorIntelligenceAgent": getattr(full_campaign_crew, 'competitor_intelligence', None),
            "ContentPersonalizationAgent": getattr(full_campaign_crew, 'content_personalization', None),
            
            # Infrastructure (3)
            "EmailWarmupAgent": getattr(full_campaign_crew, 'email_warmup', None),
            "LeadNurturingAgent": getattr(full_campaign_crew, 'lead_nurturing', None),
            "ChurnPreventionAgent": getattr(full_campaign_crew, 'churn_prevention', None),
            
            # Master Intelligence (1)
            "MasterIntelligenceAgent": self.orchestration_service.master_intelligence
        }
        
        # Filter out None values
        return {k: v for k, v in agents.items() if v is not None}

    def _is_campaign_performance_query(self, message: str) -> bool:
        """Check if the message is a campaign performance query."""
        message_lower = message.lower()
        return "campaign" in message_lower and any(keyword in message_lower for keyword in ["how", "performance", "doing"])

    def get_campaign_performance_insights(self, user_id: str) -> str:
        """
        Get performance insights for all user's campaigns using MCP tools.

        Args:
            user_id: The user's ID

        Returns:
            Formatted string with campaign performance data
        """
        try:
            # Get user's campaigns from database
            campaigns = self.db.query("SELECT id, name FROM campaigns WHERE user_id = %s", (user_id,))

            if not campaigns:
                return "You don't have any active campaigns yet. Would you like me to help you launch one?"

            insights = []
            for campaign in campaigns:
                # Use MCP tool to get performance data
                perf = self.mcp_db_tools.get_campaign_performance(campaign['id'])

                # Extract key metrics
                open_rate = perf.get('open_rate', 0)
                click_rate = perf.get('click_rate', 0)
                revenue = perf.get('revenue', 0)

                # Format insight
                insight = f"📧 {campaign['name']}: {open_rate}% open rate, {click_rate}% click rate, ${revenue} revenue"
                insights.append(insight)

            return f"Here's how your campaigns are performing:\n\n" + "\n".join(insights)

        except Exception as e:
            logger.error(f"Error retrieving campaign performance for user {user_id}: {e}")
            return "I encountered an error retrieving your campaign performance data. Please try again later."

