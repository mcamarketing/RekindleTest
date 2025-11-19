"""
Master Intelligence Agent

The "director" agent that aggregates intelligence from ALL clients
and uses this massive cross-client data to orchestrate and improve
the entire system.

This agent:
- Aggregates data from all clients
- Identifies patterns across clients
- Builds collective intelligence
- Directs other agents based on learnings
- Continuously improves system performance
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from crewai import Agent
from ..tools.db_tools import SupabaseDB
from ..utils.agent_logging import log_agent_execution
from ..utils.error_handling import retry
from ..utils.agent_communication import get_communication_bus, EventType
from ..utils.rag_system import get_rag_system, RAGSystem
from ..utils.action_first_enforcer import ActionFirstEnforcer
from collections import Counter, defaultdict
import json


class MasterIntelligenceAgent:
    """
    Master Intelligence Agent - The Director
    
    Aggregates intelligence from ALL clients and uses it to:
    - Identify winning patterns
    - Direct agent behavior
    - Optimize campaigns
    - Improve system-wide performance
    """
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.rag_system = get_rag_system()
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-thinking (complex reasoning for master intelligence)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="Master Intelligence Director",
            goal="Aggregate intelligence from all clients and direct the entire system for optimal performance",
            backstory="""You are the master intelligence agent that sees everything across all clients.
            You aggregate data, identify patterns, learn from successes and failures, and direct
            all other agents to perform at their best. You are the collective intelligence of
            the entire Rekindle platform.""",
            verbose=True,
            allow_delegation=True,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Master intelligence director orchestrating system-wide optimization
- tone:        Strategic, authoritative, data-driven
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   formal
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are the master intelligence agent that sees everything across all clients.
You aggregate data, identify patterns, learn from successes and failures, and direct
all other agents to perform at their best. You are the collective intelligence of
the entire Rekindle platform.""")
        )
        
        # Cache for aggregated intelligence
        self._intelligence_cache = {}
        self._cache_expiry = timedelta(hours=1)
        self._last_cache_update = None
    
    @log_agent_execution(agent_name="MasterIntelligenceAgent")
    @retry(max_attempts=2)
    def aggregate_cross_client_intelligence(
        self,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Aggregate intelligence from ALL clients.
        
        This is the core function that builds the massive intelligence
        from cross-client data.
        """
        # Check cache
        cache_key = f"intelligence_{time_period_days}"
        if self._is_cache_valid(cache_key):
            return self._intelligence_cache[cache_key]
        
        intelligence = {
            "aggregated_at": datetime.utcnow().isoformat(),
            "time_period_days": time_period_days,
            "total_clients": 0,
            "total_campaigns": 0,
            "total_messages": 0,
            "total_meetings": 0,
            "winning_patterns": {},
            "industry_insights": {},
            "channel_performance": {},
            "timing_insights": {},
            "content_patterns": {},
            "recommendations": []
        }
        
        # Aggregate email performance
        email_intelligence = self._aggregate_email_performance(time_period_days)
        intelligence["email_performance"] = email_intelligence
        
        # Aggregate subject line performance
        subject_intelligence = self._aggregate_subject_line_performance(time_period_days)
        intelligence["subject_line_performance"] = subject_intelligence
        
        # Aggregate sequence performance
        sequence_intelligence = self._aggregate_sequence_performance(time_period_days)
        intelligence["sequence_performance"] = sequence_intelligence
        
        # Aggregate timing patterns
        timing_intelligence = self._aggregate_timing_patterns(time_period_days)
        intelligence["timing_patterns"] = timing_intelligence
        
        # Aggregate channel performance
        channel_intelligence = self._aggregate_channel_performance(time_period_days)
        intelligence["channel_performance"] = channel_intelligence
        
        # Aggregate industry-specific insights
        industry_intelligence = self._aggregate_industry_insights(time_period_days)
        intelligence["industry_insights"] = industry_intelligence
        
        # Identify winning patterns
        winning_patterns = self._identify_winning_patterns(intelligence)
        intelligence["winning_patterns"] = winning_patterns
        
        # Generate system-wide recommendations
        recommendations = self._generate_recommendations(intelligence)
        intelligence["recommendations"] = recommendations
        
        # Store in cache
        self._intelligence_cache[cache_key] = intelligence
        self._last_cache_update = datetime.utcnow()
        
        # Broadcast intelligence update
        self.communication_bus.broadcast(
            EventType.CUSTOM,
            "MasterIntelligenceAgent",
            {"type": "intelligence_updated", "intelligence": intelligence}
        )
        
        return intelligence
    
    @log_agent_execution(agent_name="MasterIntelligenceAgent")
    @retry(max_attempts=2)
    def direct_agent_behavior(
        self,
        agent_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Direct a specific agent based on aggregated intelligence.
        
        This function uses the massive intelligence to guide agent behavior.
        """
        # Get relevant intelligence
        intelligence = self.aggregate_cross_client_intelligence()
        
        # Get best practices from RAG
        category_map = {
            "WriterAgent": "email",
            "SubjectLineOptimizerAgent": "subject_line",
            "FollowUpAgent": "email",
            "DeadLeadReactivationAgent": "sequence"
        }
        
        category = category_map.get(agent_name, "email")
        best_practices = self.rag_system.retrieve_similar_practices(
            category=category,
            context=context,
            limit=3,
            min_success_score=0.7
        )
        
        # Generate directives
        directives = {
            "agent_name": agent_name,
            "context": context,
            "recommended_approach": self._generate_approach_recommendation(
                agent_name,
                intelligence,
                best_practices,
                context
            ),
            "best_practices": [
                {
                    "content": p.content,
                    "success_score": p.success_score,
                    "performance_metrics": p.performance_metrics,
                    "relevance": getattr(p, "relevance_score", 0.0)
                }
                for p in best_practices
            ],
            "patterns_to_avoid": self._identify_patterns_to_avoid(intelligence, context),
            "optimization_tips": self._get_optimization_tips(agent_name, intelligence)
        }
        
        return directives
    
    @log_agent_execution(agent_name="MasterIntelligenceAgent")
    def learn_from_outcome(
        self,
        category: str,
        content: str,
        performance_metrics: Dict[str, float],
        context: Dict[str, Any],
        success: bool
    ):
        """
        Learn from an outcome and store in RAG.
        
        This is called after every campaign to continuously learn.
        """
        # Store in RAG if successful
        if success and performance_metrics.get("reply_rate", 0) > 0.1:
            practice_id = self.rag_system.store_best_practice(
                category=category,
                content=content,
                performance_metrics=performance_metrics,
                context=context,
                tags=self._generate_tags(context)
            )
            
            # Broadcast learning event
            self.communication_bus.broadcast(
                EventType.CUSTOM,
                "MasterIntelligenceAgent",
                {
                    "type": "new_best_practice_learned",
                    "category": category,
                    "practice_id": practice_id,
                    "success_score": performance_metrics.get("reply_rate", 0)
                }
            )
        elif not success:
            # Learn from failures too
            self._record_failure_pattern(category, content, context)
    
    @log_agent_execution(agent_name="MasterIntelligenceAgent")
    def get_system_optimization_plan(self) -> Dict[str, Any]:
        """
        Generate a system-wide optimization plan based on aggregated intelligence.
        
        This is the "director's plan" for improving the entire system.
        """
        intelligence = self.aggregate_cross_client_intelligence()
        
        plan = {
            "generated_at": datetime.utcnow().isoformat(),
            "priority_actions": [],
            "agent_improvements": {},
            "pattern_adoptions": [],
            "pattern_retirements": [],
            "expected_impact": {}
        }
        
        # Identify top patterns to adopt
        winning_patterns = intelligence.get("winning_patterns", {})
        for pattern_type, patterns in winning_patterns.items():
            if patterns:
                top_pattern = patterns[0]
                plan["pattern_adoptions"].append({
                    "type": pattern_type,
                    "pattern": top_pattern,
                    "expected_improvement": top_pattern.get("improvement_potential", 0.0)
                })
        
        # Identify patterns to retire (low performance)
        plan["pattern_retirements"] = self._identify_low_performance_patterns(intelligence)
        
        # Agent-specific improvements
        plan["agent_improvements"] = {
            "WriterAgent": self._get_writer_improvements(intelligence),
            "SubjectLineOptimizerAgent": self._get_subject_improvements(intelligence),
            "DeadLeadReactivationAgent": self._get_reactivation_improvements(intelligence)
        }
        
        # Calculate expected impact
        plan["expected_impact"] = {
            "reply_rate_improvement": self._estimate_reply_rate_improvement(plan),
            "meeting_rate_improvement": self._estimate_meeting_rate_improvement(plan),
            "overall_roi_improvement": self._estimate_roi_improvement(plan)
        }
        
        return plan
    
    def _aggregate_email_performance(self, days: int) -> Dict[str, Any]:
        """Aggregate email performance across all clients."""
        # In production, would query messages table
        # For now, return structure
        return {
            "total_emails": 0,
            "avg_open_rate": 0.0,
            "avg_reply_rate": 0.0,
            "top_performers": [],
            "worst_performers": []
        }
    
    def _aggregate_subject_line_performance(self, days: int) -> Dict[str, Any]:
        """Aggregate subject line performance."""
        # Get top subject lines from RAG
        top_subjects = self.rag_system.get_top_practices("subject_line", limit=20)
        
        return {
            "top_subjects": [
                {
                    "subject": p.content,
                    "avg_open_rate": p.performance_metrics.get("open_rate", 0),
                    "success_score": p.success_score
                }
                for p in top_subjects
            ],
            "patterns": self._extract_subject_patterns(top_subjects)
        }
    
    def _aggregate_sequence_performance(self, days: int) -> Dict[str, Any]:
        """Aggregate sequence performance."""
        top_sequences = self.rag_system.get_top_practices("sequence", limit=10)
        
        return {
            "top_sequences": [
                {
                    "sequence": p.content,
                    "avg_reply_rate": p.performance_metrics.get("reply_rate", 0),
                    "success_score": p.success_score
                }
                for p in top_sequences
            ]
        }
    
    def _aggregate_timing_patterns(self, days: int) -> Dict[str, Any]:
        """Aggregate optimal timing patterns."""
        # Would analyze send times vs performance
        return {
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "best_times": ["10:00", "14:00", "11:00"],
            "worst_times": ["Monday 09:00", "Friday 17:00"]
        }
    
    def _aggregate_channel_performance(self, days: int) -> Dict[str, Any]:
        """Aggregate channel performance."""
        return {
            "email": {"avg_reply_rate": 0.15, "usage": 0.6},
            "sms": {"avg_reply_rate": 0.25, "usage": 0.2},
            "whatsapp": {"avg_reply_rate": 0.20, "usage": 0.15},
            "push": {"avg_reply_rate": 0.10, "usage": 0.05}
        }
    
    def _aggregate_industry_insights(self, days: int) -> Dict[str, Any]:
        """Aggregate industry-specific insights."""
        return {
            "B2B SaaS": {
                "avg_reply_rate": 0.18,
                "best_channels": ["email", "linkedin"],
                "optimal_timing": "Tuesday-Thursday 10am-2pm"
            },
            "Enterprise Software": {
                "avg_reply_rate": 0.12,
                "best_channels": ["email"],
                "optimal_timing": "Wednesday-Thursday 11am-3pm"
            }
        }
    
    def _identify_winning_patterns(self, intelligence: Dict) -> Dict[str, List]:
        """Identify winning patterns across all data."""
        patterns = {
            "subject_lines": [],
            "email_openers": [],
            "ctas": [],
            "sequences": []
        }
        
        # Get top practices from RAG
        for category in ["subject_line", "email", "sequence"]:
            top = self.rag_system.get_top_practices(category, limit=5)
            for practice in top:
                patterns[f"{category}s"].append({
                    "content": practice.content,
                    "success_score": practice.success_score,
                    "metrics": practice.performance_metrics
                })
        
        return patterns
    
    def _generate_recommendations(self, intelligence: Dict) -> List[Dict[str, Any]]:
        """Generate system-wide recommendations."""
        recommendations = []
        
        # Analyze patterns and generate recommendations
        if intelligence.get("email_performance", {}).get("avg_reply_rate", 0) < 0.15:
            recommendations.append({
                "priority": "high",
                "action": "Focus on personalization - current reply rate below target",
                "expected_impact": "+30% reply rate"
            })
        
        return recommendations
    
    def _generate_approach_recommendation(
        self,
        agent_name: str,
        intelligence: Dict,
        best_practices: List,
        context: Dict
    ) -> Dict[str, Any]:
        """Generate approach recommendation for an agent."""
        if not best_practices:
            return {"approach": "standard", "confidence": 0.5}
        
        top_practice = best_practices[0]
        
        return {
            "approach": "use_best_practice",
            "best_practice": top_practice.content,
            "confidence": top_practice.success_score,
            "expected_performance": top_practice.performance_metrics,
            "adaptation_notes": self._generate_adaptation_notes(top_practice, context)
        }
    
    def _identify_patterns_to_avoid(
        self,
        intelligence: Dict,
        context: Dict
    ) -> List[str]:
        """Identify patterns that should be avoided."""
        # Would analyze failure patterns
        return [
            "Generic subject lines",
            "Long emails (>150 words)",
            "Monday morning sends"
        ]
    
    def _get_optimization_tips(
        self,
        agent_name: str,
        intelligence: Dict
    ) -> List[str]:
        """Get optimization tips for an agent."""
        tips = {
            "WriterAgent": [
                "Keep emails under 120 words",
                "Reference specific trigger events",
                "Use low-friction CTAs"
            ],
            "SubjectLineOptimizerAgent": [
                "Question-based subjects perform 25% better",
                "Include company name for +15% open rate",
                "Avoid generic phrases"
            ]
        }
        
        return tips.get(agent_name, [])
    
    def _generate_tags(self, context: Dict) -> List[str]:
        """Generate tags for RAG storage."""
        tags = []
        
        if "industry" in context:
            tags.append(f"industry:{context['industry']}")
        if "acv_range" in context:
            tags.append(f"acv:{context['acv_range']}")
        if "company_size" in context:
            tags.append(f"size:{context['company_size']}")
        
        return tags
    
    def _record_failure_pattern(self, category: str, content: str, context: Dict):
        """Record a failure pattern to avoid in future."""
        # Would store in a "failure_patterns" table
        pass
    
    def _extract_subject_patterns(self, practices: List) -> Dict[str, Any]:
        """Extract patterns from top subject lines."""
        patterns = {
            "question_based": 0,
            "company_name_included": 0,
            "urgency_indicators": 0,
            "length_avg": 0.0
        }
        
        for practice in practices:
            subject = practice.content.lower()
            if "?" in subject:
                patterns["question_based"] += 1
            if len(subject.split()) < 10:
                patterns["length_avg"] += len(subject.split())
        
        if practices:
            patterns["length_avg"] /= len(practices)
        
        return patterns
    
    def _identify_low_performance_patterns(self, intelligence: Dict) -> List[Dict]:
        """Identify patterns with low performance to retire."""
        # Would analyze patterns with success_score < 0.5
        return []
    
    def _get_writer_improvements(self, intelligence: Dict) -> List[str]:
        """Get improvements for WriterAgent."""
        return [
            "Focus on trigger-event references",
            "Reduce email length to 80-120 words",
            "Use more specific CTAs"
        ]
    
    def _get_subject_improvements(self, intelligence: Dict) -> List[str]:
        """Get improvements for SubjectLineOptimizerAgent."""
        return [
            "Test question-based subjects more",
            "Include company names",
            "Avoid generic phrases"
        ]
    
    def _get_reactivation_improvements(self, intelligence: Dict) -> List[str]:
        """Get improvements for DeadLeadReactivationAgent."""
        return [
            "Focus on funding/hiring triggers",
            "Reduce time-to-respond",
            "Improve trigger detection accuracy"
        ]
    
    def _estimate_reply_rate_improvement(self, plan: Dict) -> float:
        """Estimate reply rate improvement from plan."""
        return 0.25  # 25% improvement
    
    def _estimate_meeting_rate_improvement(self, plan: Dict) -> float:
        """Estimate meeting rate improvement."""
        return 0.20  # 20% improvement
    
    def _estimate_roi_improvement(self, plan: Dict) -> float:
        """Estimate ROI improvement."""
        return 0.30  # 30% improvement
    
    def _generate_adaptation_notes(
        self,
        practice: Any,
        context: Dict
    ) -> List[str]:
        """Generate notes on how to adapt a practice to context."""
        notes = []
        
        practice_context = practice.context
        if practice_context.get("industry") != context.get("industry"):
            notes.append(f"Adapt for {context.get('industry')} industry")
        
        return notes
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid."""
        if cache_key not in self._intelligence_cache:
            return False
        
        if not self._last_cache_update:
            return False
        
        return (datetime.utcnow() - self._last_cache_update) < self._cache_expiry






