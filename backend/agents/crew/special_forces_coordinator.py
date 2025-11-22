"""
SpecialForcesCoordinator - Multi-Agent Crew Orchestration

Coordinates multiple specialized agents to execute complex multi-step missions,
manages agent dependencies, orchestrates workflows, and ensures mission success.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .base_agent import BaseAgent, MissionContext, AgentResult
from .reviver_agent import ReviverAgent
from .deliverability_agent import DeliverabilityAgent
from .personalizer_agent import PersonalizerAgent
from .icp_intelligence_agent import ICPIntelligenceAgent
from .scraper_agent import ScraperAgent
from .outreach_agent import OutreachAgent
from .analytics_agent import AnalyticsAgent

logger = logging.getLogger(__name__)


class WorkflowPhase(str, Enum):
    """Workflow execution phases"""
    PLANNING = 'planning'
    INTELLIGENCE = 'intelligence'
    PREPARATION = 'preparation'
    EXECUTION = 'execution'
    ANALYSIS = 'analysis'
    OPTIMIZATION = 'optimization'
    COMPLETED = 'completed'


@dataclass
class AgentTask:
    """Task for a specialized agent"""
    agent_name: str
    task_type: str
    params: Dict[str, Any]
    dependencies: List[str]  # Task IDs this depends on
    status: str = 'pending'  # pending, in_progress, completed, failed
    result: Optional[AgentResult] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class SpecialForcesCoordinator(BaseAgent):
    """
    Master coordinator for multi-agent crew orchestration.

    Capabilities:
    - Multi-agent workflow orchestration
    - Dependency management and sequencing
    - Parallel execution coordination
    - Error handling and recovery
    - Resource allocation
    - Progress tracking and reporting
    - Mission success validation
    """

    def __init__(self, supabase, redis_client=None, openai_api_key=None):
        super().__init__(
            agent_name="SpecialForcesCoordinator",
            supabase=supabase,
            redis_client=redis_client,
            openai_api_key=openai_api_key
        )

        # Initialize specialized agents
        self.agents = {
            'ReviverAgent': ReviverAgent(supabase, redis_client, openai_api_key),
            'DeliverabilityAgent': DeliverabilityAgent(supabase, redis_client, openai_api_key),
            'PersonalizerAgent': PersonalizerAgent(supabase, redis_client, openai_api_key),
            'ICPIntelligenceAgent': ICPIntelligenceAgent(supabase, redis_client, openai_api_key),
            'ScraperAgent': ScraperAgent(supabase, redis_client, openai_api_key),
            'OutreachAgent': OutreachAgent(supabase, redis_client, openai_api_key),
            'AnalyticsAgent': AnalyticsAgent(supabase, redis_client, openai_api_key),
        }

        # Workflow templates
        self.WORKFLOW_TEMPLATES = {
            'lead_reactivation_campaign': self._build_reactivation_workflow,
            'new_campaign_launch': self._build_campaign_launch_workflow,
            'campaign_optimization': self._build_optimization_workflow,
            'icp_discovery': self._build_icp_discovery_workflow,
        }

    async def handle_mission(self, context: MissionContext) -> AgentResult:
        """Execute coordinated multi-agent mission"""
        logger.info(f"SpecialForcesCoordinator starting mission {context.mission_id}")

        # Get workflow parameters
        workflow_type = context.custom_params.get('workflow_type', 'new_campaign_launch')
        workflow_params = context.custom_params.get('workflow_params', {})

        # Step 1: Build workflow from template
        workflow_tasks = await self._build_workflow(workflow_type, workflow_params, context)
        logger.info(f"Built workflow with {len(workflow_tasks)} tasks")

        # Step 2: Execute workflow with dependency management
        execution_results = await self._execute_workflow(workflow_tasks, context)

        # Step 3: Validate mission success
        mission_success = await self._validate_mission_success(execution_results)

        # Step 4: Generate mission report
        mission_report = await self._generate_mission_report(
            workflow_tasks,
            execution_results,
            mission_success
        )

        # Build result
        result_data = {
            'workflow_type': workflow_type,
            'total_tasks': len(workflow_tasks),
            'tasks_completed': len([t for t in workflow_tasks if t.status == 'completed']),
            'tasks_failed': len([t for t in workflow_tasks if t.status == 'failed']),
            'mission_success': mission_success,
            'execution_summary': mission_report,
            'task_breakdown': [
                {
                    'agent': t.agent_name,
                    'task_type': t.task_type,
                    'status': t.status,
                    'duration_seconds': (
                        (t.completed_at - t.started_at).total_seconds()
                        if t.started_at and t.completed_at else None
                    ),
                }
                for t in workflow_tasks
            ],
        }

        return AgentResult(
            success=mission_success,
            data=result_data,
            message=f"Workflow '{workflow_type}' completed: {result_data['tasks_completed']}/{len(workflow_tasks)} tasks successful"
        )

    async def _build_workflow(
        self,
        workflow_type: str,
        workflow_params: Dict[str, Any],
        context: MissionContext
    ) -> List[AgentTask]:
        """Build workflow from template"""
        template_builder = self.WORKFLOW_TEMPLATES.get(workflow_type)

        if not template_builder:
            logger.error(f"Unknown workflow type: {workflow_type}")
            return []

        return template_builder(workflow_params, context)

    def _build_reactivation_workflow(
        self,
        params: Dict[str, Any],
        context: MissionContext
    ) -> List[AgentTask]:
        """Build lead reactivation campaign workflow"""
        tasks = []

        # Task 1: Check domain health
        tasks.append(AgentTask(
            agent_name='DeliverabilityAgent',
            task_type='domain_health_check',
            params={},
            dependencies=[],
        ))

        # Task 2: Enrich lead data (depends on nothing)
        tasks.append(AgentTask(
            agent_name='ScraperAgent',
            task_type='lead_enrichment',
            params={
                'lead_ids': params.get('lead_ids', []),
                'fields': ['all'],
                'max_cost': 5.0,
            },
            dependencies=[],
        ))

        # Task 3: Score and filter leads (depends on enrichment)
        tasks.append(AgentTask(
            agent_name='ReviverAgent',
            task_type='lead_reactivation',
            params={
                'lead_ids': params.get('lead_ids', []),
            },
            dependencies=['ScraperAgent'],
        ))

        # Task 4: Generate personalized messages (depends on reviver)
        tasks.append(AgentTask(
            agent_name='PersonalizerAgent',
            task_type='message_personalization',
            params={
                'lead_ids': params.get('lead_ids', []),
                'template_type': 'reactivation',
                'channel': 'email',
                'framework': 'pas',
                'generate_variants': True,
            },
            dependencies=['ReviverAgent'],
        ))

        # Task 5: Execute outreach (depends on personalizer and deliverability)
        tasks.append(AgentTask(
            agent_name='OutreachAgent',
            task_type='message_delivery',
            params={
                'campaign_id': params.get('campaign_id'),
                'channel': 'email',
                'immediate': False,
            },
            dependencies=['PersonalizerAgent', 'DeliverabilityAgent'],
        ))

        # Task 6: Track and analyze (depends on outreach)
        tasks.append(AgentTask(
            agent_name='AnalyticsAgent',
            task_type='campaign_analysis',
            params={
                'campaign_ids': [params.get('campaign_id')],
                'time_range_days': 7,
                'include_recommendations': True,
            },
            dependencies=['OutreachAgent'],
        ))

        return tasks

    def _build_campaign_launch_workflow(
        self,
        params: Dict[str, Any],
        context: MissionContext
    ) -> List[AgentTask]:
        """Build new campaign launch workflow"""
        tasks = []

        # Task 1: Analyze ICP
        tasks.append(AgentTask(
            agent_name='ICPIntelligenceAgent',
            task_type='icp_analysis',
            params={},
            dependencies=[],
        ))

        # Task 2: Enrich target leads
        tasks.append(AgentTask(
            agent_name='ScraperAgent',
            task_type='lead_enrichment',
            params={
                'lead_ids': params.get('lead_ids', []),
                'max_cost': 10.0,
            },
            dependencies=[],
        ))

        # Task 3: Check domain health
        tasks.append(AgentTask(
            agent_name='DeliverabilityAgent',
            task_type='domain_health_check',
            params={},
            dependencies=[],
        ))

        # Task 4: Generate personalized messages
        tasks.append(AgentTask(
            agent_name='PersonalizerAgent',
            task_type='message_personalization',
            params={
                'lead_ids': params.get('lead_ids', []),
                'template_type': params.get('template_type', 'cold_outreach'),
                'channel': params.get('channel', 'email'),
                'framework': params.get('framework', 'aida'),
            },
            dependencies=['ICPIntelligenceAgent', 'ScraperAgent'],
        ))

        # Task 5: Execute outreach
        tasks.append(AgentTask(
            agent_name='OutreachAgent',
            task_type='message_delivery',
            params={
                'campaign_id': params.get('campaign_id'),
                'channel': params.get('channel', 'email'),
            },
            dependencies=['PersonalizerAgent', 'DeliverabilityAgent'],
        ))

        return tasks

    def _build_optimization_workflow(
        self,
        params: Dict[str, Any],
        context: MissionContext
    ) -> List[AgentTask]:
        """Build campaign optimization workflow"""
        tasks = []

        # Task 1: Analyze current performance
        tasks.append(AgentTask(
            agent_name='AnalyticsAgent',
            task_type='campaign_analysis',
            params={
                'campaign_ids': params.get('campaign_ids', []),
                'time_range_days': 30,
                'include_recommendations': True,
                'analyze_ab_tests': True,
            },
            dependencies=[],
        ))

        # Task 2: Check domain health
        tasks.append(AgentTask(
            agent_name='DeliverabilityAgent',
            task_type='domain_health_check',
            params={},
            dependencies=[],
        ))

        return tasks

    def _build_icp_discovery_workflow(
        self,
        params: Dict[str, Any],
        context: MissionContext
    ) -> List[AgentTask]:
        """Build ICP discovery workflow"""
        tasks = []

        # Task 1: Analyze existing customers
        tasks.append(AgentTask(
            agent_name='ICPIntelligenceAgent',
            task_type='icp_analysis',
            params={},
            dependencies=[],
        ))

        # Task 2: Enrich customer data
        tasks.append(AgentTask(
            agent_name='ScraperAgent',
            task_type='customer_enrichment',
            params={
                'max_cost': 20.0,
            },
            dependencies=[],
        ))

        # Task 3: Re-analyze with enriched data
        tasks.append(AgentTask(
            agent_name='ICPIntelligenceAgent',
            task_type='icp_analysis',
            params={},
            dependencies=['ScraperAgent'],
        ))

        return tasks

    async def _execute_workflow(
        self,
        tasks: List[AgentTask],
        context: MissionContext
    ) -> Dict[str, AgentResult]:
        """Execute workflow with dependency management"""
        execution_results = {}
        completed_tasks: Set[str] = set()
        failed_tasks: Set[str] = set()

        max_iterations = len(tasks) * 2  # Prevent infinite loops
        iteration = 0

        while len(completed_tasks) + len(failed_tasks) < len(tasks) and iteration < max_iterations:
            iteration += 1

            # Find tasks ready to execute (dependencies met)
            ready_tasks = self._get_ready_tasks(tasks, completed_tasks, failed_tasks)

            if not ready_tasks:
                logger.warning("No tasks ready to execute, checking for deadlock")
                break

            # Execute ready tasks (could be parallelized in production)
            for task in ready_tasks:
                result = await self._execute_agent_task(task, context, execution_results)
                execution_results[task.agent_name] = result

                if result.success:
                    task.status = 'completed'
                    completed_tasks.add(task.agent_name)
                else:
                    task.status = 'failed'
                    failed_tasks.add(task.agent_name)

                    # Check if failure is critical
                    if self._is_critical_task(task):
                        logger.error(f"Critical task {task.agent_name} failed, aborting workflow")
                        # Mark remaining tasks as failed
                        for remaining_task in tasks:
                            if remaining_task.status == 'pending':
                                remaining_task.status = 'failed'
                        return execution_results

        return execution_results

    def _get_ready_tasks(
        self,
        tasks: List[AgentTask],
        completed_tasks: Set[str],
        failed_tasks: Set[str]
    ) -> List[AgentTask]:
        """Get tasks ready to execute (all dependencies met)"""
        ready = []

        for task in tasks:
            # Skip if already processed
            if task.status != 'pending':
                continue

            # Check if all dependencies are completed
            dependencies_met = all(
                dep in completed_tasks for dep in task.dependencies
            )

            # Check if any dependencies failed
            dependencies_failed = any(
                dep in failed_tasks for dep in task.dependencies
            )

            if dependencies_failed:
                task.status = 'failed'
                task.result = AgentResult(
                    success=False,
                    data={},
                    message=f"Dependency failed: {task.dependencies}"
                )
                continue

            if dependencies_met:
                ready.append(task)

        return ready

    async def _execute_agent_task(
        self,
        task: AgentTask,
        context: MissionContext,
        previous_results: Dict[str, AgentResult]
    ) -> AgentResult:
        """Execute a single agent task"""
        logger.info(f"Executing task: {task.agent_name} - {task.task_type}")

        task.status = 'in_progress'
        task.started_at = datetime.utcnow()

        try:
            # Get agent instance
            agent = self.agents.get(task.agent_name)

            if not agent:
                raise ValueError(f"Unknown agent: {task.agent_name}")

            # Build task context with previous results
            task_context = MissionContext(
                mission_id=f"{context.mission_id}_{task.agent_name}",
                user_id=context.user_id,
                custom_params=task.params
            )

            # Merge in results from dependencies
            for dep_agent_name in task.dependencies:
                if dep_agent_name in previous_results:
                    dep_result = previous_results[dep_agent_name]
                    task_context.custom_params[f'{dep_agent_name}_result'] = dep_result.data

            # Execute agent mission
            result = await agent.handle_mission(task_context)

            task.completed_at = datetime.utcnow()
            task.result = result

            logger.info(f"Task completed: {task.agent_name} - Success: {result.success}")

            return result

        except Exception as e:
            logger.error(f"Task failed: {task.agent_name} - {e}")
            task.completed_at = datetime.utcnow()

            result = AgentResult(
                success=False,
                data={},
                message=f"Task execution failed: {str(e)}"
            )

            task.result = result
            return result

    def _is_critical_task(self, task: AgentTask) -> bool:
        """Determine if task is critical for mission success"""
        # In this implementation, DeliverabilityAgent and OutreachAgent are critical
        return task.agent_name in ['DeliverabilityAgent', 'OutreachAgent']

    async def _validate_mission_success(
        self,
        execution_results: Dict[str, AgentResult]
    ) -> bool:
        """Validate overall mission success"""
        # Mission succeeds if all critical agents succeeded
        critical_agents = ['DeliverabilityAgent', 'OutreachAgent']

        for critical_agent in critical_agents:
            if critical_agent in execution_results:
                if not execution_results[critical_agent].success:
                    return False

        # At least one agent must have succeeded
        return any(result.success for result in execution_results.values())

    async def _generate_mission_report(
        self,
        workflow_tasks: List[AgentTask],
        execution_results: Dict[str, AgentResult],
        mission_success: bool
    ) -> Dict[str, Any]:
        """Generate comprehensive mission report"""
        total_duration = sum(
            (t.completed_at - t.started_at).total_seconds()
            for t in workflow_tasks
            if t.started_at and t.completed_at
        )

        report = {
            'mission_success': mission_success,
            'total_duration_seconds': round(total_duration, 2),
            'tasks_summary': {
                'total': len(workflow_tasks),
                'completed': len([t for t in workflow_tasks if t.status == 'completed']),
                'failed': len([t for t in workflow_tasks if t.status == 'failed']),
                'pending': len([t for t in workflow_tasks if t.status == 'pending']),
            },
            'agent_results': {
                agent_name: {
                    'success': result.success,
                    'message': result.message,
                    'data_summary': self._summarize_agent_data(result.data),
                }
                for agent_name, result in execution_results.items()
            },
            'bottlenecks': self._identify_bottlenecks(workflow_tasks),
        }

        return report

    def _summarize_agent_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize agent result data (remove large fields)"""
        summary = {}

        # Include only key metrics
        key_fields = [
            'total', 'count', 'success', 'failed', 'rate',
            'score', 'cost', 'roi', 'leads', 'campaigns', 'messages'
        ]

        for key, value in data.items():
            # Include if key contains any key field
            if any(kf in key.lower() for kf in key_fields):
                summary[key] = value

        return summary

    def _identify_bottlenecks(self, workflow_tasks: List[AgentTask]) -> List[Dict[str, Any]]:
        """Identify workflow bottlenecks"""
        bottlenecks = []

        for task in workflow_tasks:
            if not task.started_at or not task.completed_at:
                continue

            duration = (task.completed_at - task.started_at).total_seconds()

            # Flag tasks taking > 30 seconds
            if duration > 30:
                bottlenecks.append({
                    'agent': task.agent_name,
                    'task_type': task.task_type,
                    'duration_seconds': round(duration, 2),
                    'status': task.status,
                })

        return bottlenecks
