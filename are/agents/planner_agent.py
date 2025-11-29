"""
ARE Planner Agent

Breaks high-level user goals into executable tasks, builds execution plans,
determines agent selection heuristics, and outputs structured plan objects.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """Represents a single executable task"""
    id: str
    description: str
    agent_type: str
    capabilities: List[str]
    input_data: Dict[str, Any]
    priority: int = 1
    estimated_duration: int = 300  # seconds
    dependencies: List[str] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionPlan:
    """Complete execution plan for a user goal"""
    plan_id: str
    goal: Dict[str, Any]
    tasks: List[Task]
    dependencies: List[Dict[str, str]]  # [{"from": "task1", "to": "task2"}]
    agent_assignments: Dict[str, str]  # task_id -> agent_cluster
    risk_assessment: Dict[str, Any]
    estimated_completion: datetime
    created_at: datetime

class PlannerAgent:
    """ARE Planner Agent - Goal decomposition and planning"""

    def __init__(self):
        self.agent_capabilities = {
            "brain": ["content_generation", "strategic_analysis", "campaign_planning", "persona_inference"],
            "crewai": ["lead_research", "content_writing", "meeting_booking", "compliance_checking"],
            "rex": ["real_time_decisions", "outcome_tracking", "resource_allocation"],
            "services": ["revival_engine", "leakage_detection", "revenue_forecasting", "icp_generation"]
        }

    async def run(self, input_data: Dict[str, Any], context: Any) -> ExecutionPlan:
        """Main planning execution method"""
        logger.info(f"Planning execution for goal: {input_data.get('description', 'Unknown')}")

        goal = input_data

        # Step 0: Check for clarifying questions needed
        clarifying_questions = await self._check_clarifying_questions(goal)
        if clarifying_questions:
            # Return special response indicating clarifying questions needed
            return {
                "status": "clarifying_questions_needed",
                "questions": clarifying_questions,
                "goal_summary": goal.get('description', 'Unknown goal')
            }

        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(goal)) % 10000}"

        try:
            # Step 1: Analyze goal and extract requirements
            goal_analysis = await self._analyze_goal(goal)

            # Step 2: Decompose goal into tasks
            tasks = await self._decompose_goal(goal, goal_analysis)

            # Step 3: Determine task dependencies
            dependencies = self._build_dependencies(tasks)

            # Step 4: Assign tasks to agent clusters
            agent_assignments = await self._assign_agents(tasks, goal_analysis)

            # Step 5: Assess execution risks
            risk_assessment = await self._assess_risks(tasks, agent_assignments)

            # Step 6: Estimate completion time
            estimated_completion = self._estimate_completion(tasks, dependencies)

            # Create execution plan
            plan = ExecutionPlan(
                plan_id=plan_id,
                goal=goal,
                tasks=tasks,
                dependencies=dependencies,
                agent_assignments=agent_assignments,
                risk_assessment=risk_assessment,
                estimated_completion=estimated_completion,
                created_at=datetime.now()
            )

            logger.info(f"Generated execution plan {plan_id} with {len(tasks)} tasks")
            return plan

        except Exception as e:
            logger.error(f"Planning failed: {e}")
            raise

    async def _check_clarifying_questions(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if clarifying questions are needed before planning"""
        questions = []

        # Check for goal type
        if not goal.get("goal_type"):
            questions.append({
                "question": "What type of revenue goal are you trying to achieve?",
                "field": "goal_type",
                "options": ["REVIVE_PIPELINE", "INCREASE_MEETINGS", "OPTIMIZE_SEQUENCE", "BUILD_ICP"],
                "required": True
            })

        # Check for target metrics
        target_metrics = goal.get("target_metrics", {})
        if not target_metrics:
            questions.append({
                "question": "What are your target metrics for this goal?",
                "field": "target_metrics",
                "examples": ["meetings: 20", "leads: 100", "revenue: 50000"],
                "required": True
            })

        # Check for specific constraints
        constraints = goal.get("constraints", {})
        if not constraints.get("budget"):
            questions.append({
                "question": "What's your budget for this initiative?",
                "field": "constraints.budget",
                "examples": ["5000", "15000", "unlimited"],
                "required": False
            })

        if not constraints.get("timeline"):
            questions.append({
                "question": "What's your timeline for achieving this goal?",
                "field": "constraints.timeline",
                "examples": ["2 weeks", "1 month", "3 months"],
                "required": False
            })

        # Goal-specific questions
        goal_type = goal.get("goal_type")
        if goal_type == "REVIVE_PIPELINE":
            if not target_metrics.get("segment"):
                questions.append({
                    "question": "Which lead segment do you want to revive?",
                    "field": "target_metrics.segment",
                    "options": ["dormant_30_days", "dormant_90_days", "cold_leads"],
                    "required": True
                })
        elif goal_type == "INCREASE_MEETINGS":
            if not target_metrics.get("current_conversion"):
                questions.append({
                    "question": "What's your current reply-to-meeting conversion rate?",
                    "field": "target_metrics.current_conversion",
                    "examples": ["5%", "10%", "15%"],
                    "required": False
                })

        return questions

    async def _analyze_goal(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze goal to understand requirements and constraints"""
        goal_type = goal.get("goal_type", "GENERAL")
        description = goal.get("description", "")
        target_metrics = goal.get("target_metrics", {})
        constraints = goal.get("constraints", {})

        analysis = {
            "goal_type": goal_type,
            "complexity": self._assess_complexity(goal),
            "required_capabilities": self._extract_capabilities(goal),
            "timeline_sensitivity": self._assess_timeline_sensitivity(goal),
            "risk_factors": self._identify_risk_factors(goal),
            "resource_requirements": self._estimate_resources(goal)
        }

        logger.debug(f"Goal analysis: {analysis}")
        return analysis

    async def _decompose_goal(self, goal: Dict[str, Any], analysis: Dict[str, Any]) -> List[Task]:
        """Break down goal into executable tasks"""
        tasks = []
        task_counter = 0

        goal_type = goal.get("goal_type")

        if goal_type == "REVIVE_PIPELINE":
            tasks.extend(await self._create_revive_pipeline_tasks(goal, analysis, task_counter))
        elif goal_type == "INCREASE_MEETINGS":
            tasks.extend(await self._create_increase_meetings_tasks(goal, analysis, task_counter))
        elif goal_type == "OPTIMIZE_SEQUENCE":
            tasks.extend(await self._create_optimize_sequence_tasks(goal, analysis, task_counter))
        elif goal_type == "BUILD_ICP":
            tasks.extend(await self._create_build_icp_tasks(goal, analysis, task_counter))
        else:
            # Generic goal decomposition
            tasks.extend(await self._create_generic_tasks(goal, analysis, task_counter))

        return tasks

    async def _create_revive_pipeline_tasks(self, goal: Dict[str, Any], analysis: Dict[str, Any], start_id: int) -> List[Task]:
        """Create tasks for pipeline revival goal"""
        tasks = []

        # Task 1: Research dormant leads
        tasks.append(Task(
            id=f"task_{start_id + 1}",
            description="Research dormant leads for revival opportunities",
            agent_type="crewai",
            capabilities=["lead_research"],
            input_data={
                "segment": goal.get("segment", "dormant"),
                "criteria": {"last_activity_days": 30}
            },
            priority=3,
            estimated_duration=600
        ))

        # Task 2: Generate personalized revival content
        tasks.append(Task(
            id=f"task_{start_id + 2}",
            description="Generate personalized revival messages",
            agent_type="brain",
            capabilities=["content_generation"],
            input_data={
                "objective": "revival",
                "tone": "professional",
                "personalization_level": "high"
            },
            priority=2,
            estimated_duration=300,
            dependencies=[f"task_{start_id + 1}"]
        ))

        # Task 3: Optimize send timing
        tasks.append(Task(
            id=f"task_{start_id + 3}",
            description="Optimize send timing for revival campaigns",
            agent_type="crewai",
            capabilities=["timing_optimization"],
            input_data={"campaign_type": "revival"},
            priority=2,
            estimated_duration=180,
            dependencies=[f"task_{start_id + 1}"]
        ))

        # Task 4: Execute revival campaign
        tasks.append(Task(
            id=f"task_{start_id + 4}",
            description="Execute revival campaign with optimized content and timing",
            agent_type="crewai",
            capabilities=["campaign_execution"],
            input_data={"campaign_type": "revival"},
            priority=1,
            estimated_duration=900,
            dependencies=[f"task_{start_id + 2}", f"task_{start_id + 3}"]
        ))

        return tasks

    async def _create_increase_meetings_tasks(self, goal: Dict[str, Any], analysis: Dict[str, Any], start_id: int) -> List[Task]:
        """Create tasks for increasing meetings goal"""
        tasks = []

        # Task 1: Analyze current conversion funnel
        tasks.append(Task(
            id=f"task_{start_id + 1}",
            description="Analyze current reply-to-meeting conversion rates",
            agent_type="rex",
            capabilities=["analytics"],
            input_data={"analysis_type": "conversion_funnel"},
            priority=3,
            estimated_duration=300
        ))

        # Task 2: Optimize follow-up sequences
        tasks.append(Task(
            id=f"task_{start_id + 2}",
            description="Optimize follow-up sequences for better conversion",
            agent_type="brain",
            capabilities=["sequence_optimization"],
            input_data={"objective": "meeting_conversion"},
            priority=2,
            estimated_duration=600,
            dependencies=[f"task_{start_id + 1}"]
        ))

        # Task 3: Enhance objection handling
        tasks.append(Task(
            id=f"task_{start_id + 3}",
            description="Improve objection handling responses",
            agent_type="crewai",
            capabilities=["objection_handling"],
            input_data={"focus_area": "meeting_requests"},
            priority=2,
            estimated_duration=450,
            dependencies=[f"task_{start_id + 1}"]
        ))

        # Task 4: Execute optimized sequences
        tasks.append(Task(
            id=f"task_{start_id + 4}",
            description="Execute optimized meeting conversion sequences",
            agent_type="crewai",
            capabilities=["sequence_execution"],
            input_data={"optimization_type": "meeting_focus"},
            priority=1,
            estimated_duration=1200,
            dependencies=[f"task_{start_id + 2}", f"task_{start_id + 3}"]
        ))

        return tasks

    async def _create_generic_tasks(self, goal: Dict[str, Any], analysis: Dict[str, Any], start_id: int) -> List[Task]:
        """Create generic tasks for unspecified goal types"""
        tasks = []

        # Task 1: Research and analysis
        tasks.append(Task(
            id=f"task_{start_id + 1}",
            description="Research and analyze target audience",
            agent_type="crewai",
            capabilities=["lead_research", "market_analysis"],
            input_data={"goal_context": goal},
            priority=3,
            estimated_duration=600
        ))

        # Task 2: Content generation
        tasks.append(Task(
            id=f"task_{start_id + 2}",
            description="Generate personalized content and messaging",
            agent_type="brain",
            capabilities=["content_generation"],
            input_data={"goal_context": goal},
            priority=2,
            estimated_duration=450,
            dependencies=[f"task_{start_id + 1}"]
        ))

        # Task 3: Campaign execution
        tasks.append(Task(
            id=f"task_{start_id + 3}",
            description="Execute optimized campaign",
            agent_type="crewai",
            capabilities=["campaign_execution"],
            input_data={"goal_context": goal},
            priority=1,
            estimated_duration=900,
            dependencies=[f"task_{start_id + 2}"]
        ))

        return tasks

    def _build_dependencies(self, tasks: List[Task]) -> List[Dict[str, str]]:
        """Build task dependency graph"""
        dependencies = []

        # For now, use explicit dependencies from task definitions
        # In a more sophisticated implementation, this could analyze task relationships
        for task in tasks:
            for dep in task.dependencies:
                dependencies.append({"from": dep, "to": task.id})

        return dependencies

    async def _assign_agents(self, tasks: List[Task], analysis: Dict[str, Any]) -> Dict[str, str]:
        """Assign tasks to appropriate agent clusters"""
        assignments = {}

        for task in tasks:
            # Match task capabilities to agent cluster capabilities
            best_agent = self._find_best_agent_for_task(task, analysis)
            assignments[task.id] = best_agent

        return assignments

    def _find_best_agent_for_task(self, task: Task, analysis: Dict[str, Any]) -> str:
        """Find the best agent cluster for a given task"""
        # Score each agent cluster based on capability match
        scores = {}

        for agent_cluster, capabilities in self.agent_capabilities.items():
            score = 0
            for required_cap in task.capabilities:
                if required_cap in capabilities:
                    score += 1
            scores[agent_cluster] = score

        # Return agent with highest score
        return max(scores, key=scores.get)

    async def _assess_risks(self, tasks: List[Task], assignments: Dict[str, str]) -> Dict[str, Any]:
        """Assess execution risks"""
        risk_factors = []
        risk_score = 0.0

        # Check for high-risk task combinations
        brain_tasks = sum(1 for task_id, agent in assignments.items() if agent == "brain")
        if brain_tasks > 3:
            risk_factors.append("High LLM usage may exceed rate limits")
            risk_score += 0.3

        # Check for complex dependencies
        max_deps = max(len(task.dependencies) for task in tasks)
        if max_deps > 2:
            risk_factors.append("Complex task dependencies may cause delays")
            risk_score += 0.2

        # Check for timeline constraints
        total_duration = sum(task.estimated_duration for task in tasks)
        if total_duration > 3600:  # 1 hour
            risk_factors.append("Long execution time increases failure risk")
            risk_score += 0.1

        return {
            "score": min(risk_score, 1.0),
            "level": "HIGH" if risk_score > 0.7 else "MEDIUM" if risk_score > 0.3 else "LOW",
            "factors": risk_factors,
            "mitigations": self._suggest_mitigations(risk_factors)
        }

    def _estimate_completion(self, tasks: List[Task], dependencies: List[Dict[str, str]]) -> datetime:
        """Estimate plan completion time"""
        # Simple estimation: sequential execution
        total_duration = sum(task.estimated_duration for task in tasks)

        # Add parallelization factor (assume 30% overlap)
        parallel_factor = 0.7
        adjusted_duration = total_duration * parallel_factor

        return datetime.now() + asyncio.timedelta(seconds=adjusted_duration)

    def _assess_complexity(self, goal: Dict[str, Any]) -> str:
        """Assess goal complexity"""
        target_metrics = goal.get("target_metrics", {})
        constraints = goal.get("constraints", {})

        complexity_score = 0

        # More target metrics = higher complexity
        complexity_score += len(target_metrics) * 0.2

        # Strict constraints = higher complexity
        if constraints.get("autonomy_level") == "L0":
            complexity_score += 0.3
        if constraints.get("max_budget"):
            complexity_score += 0.1

        if complexity_score > 0.8:
            return "HIGH"
        elif complexity_score > 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def _extract_capabilities(self, goal: Dict[str, Any]) -> List[str]:
        """Extract required capabilities from goal"""
        goal_type = goal.get("goal_type", "")
        capabilities = []

        if "REVIVE" in goal_type:
            capabilities.extend(["lead_research", "content_generation", "campaign_execution"])
        elif "MEETING" in goal_type:
            capabilities.extend(["sequence_optimization", "objection_handling", "analytics"])
        elif "ICP" in goal_type:
            capabilities.extend(["market_analysis", "segmentation", "persona_inference"])

        return capabilities

    def _assess_timeline_sensitivity(self, goal: Dict[str, Any]) -> str:
        """Assess timeline sensitivity"""
        deadline = goal.get("deadline")
        if not deadline:
            return "LOW"

        # Calculate days until deadline
        if isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))

        days_until = (deadline - datetime.now()).days

        if days_until < 1:
            return "CRITICAL"
        elif days_until < 7:
            return "HIGH"
        elif days_until < 30:
            return "MEDIUM"
        else:
            return "LOW"

    def _identify_risk_factors(self, goal: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors"""
        risks = []

        constraints = goal.get("constraints", {})
        if constraints.get("autonomy_level") == "L0":
            risks.append("Manual approval required for all actions")

        if constraints.get("max_budget", 0) < 1000:
            risks.append("Limited budget may constrain execution")

        target_metrics = goal.get("target_metrics", {})
        if target_metrics.get("meetings", 0) > 50:
            risks.append("High meeting target may strain resources")

        return risks

    def _estimate_resources(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resource requirements"""
        target_metrics = goal.get("target_metrics", {})

        return {
            "estimated_leads": target_metrics.get("leads", 100),
            "estimated_emails": target_metrics.get("emails", 500),
            "estimated_meetings": target_metrics.get("meetings", 10),
            "estimated_duration_hours": 8  # Default estimate
        }

    def _suggest_mitigations(self, risk_factors: List[str]) -> List[str]:
        """Suggest risk mitigations"""
        mitigations = []

        for risk in risk_factors:
            if "rate limits" in risk:
                mitigations.append("Implement request batching and queuing")
            elif "dependencies" in risk:
                mitigations.append("Break complex tasks into smaller units")
            elif "execution time" in risk:
                mitigations.append("Implement parallel processing where possible")

        return mitigations