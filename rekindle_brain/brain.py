"""
Rekindle Brain - Main Orchestration Class

The central intelligence system that coordinates model management, training, inference,
and agent integration for business decision making.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass

from .config import BrainConfig, ModelType, DeploymentType
from .models import ModelManager
from .training import BrainTrainer
from .inference import BrainInference
from .data import DataPipeline
from .security import SecurityManager
from .agent_integration import AgentIntegrator

logger = logging.getLogger(__name__)

@dataclass
class BusinessQuery:
    """A business intelligence query"""
    task_type: str
    goal: str
    context: Dict[str, Any]
    constraints: Dict[str, Any]
    social_intel: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class BrainResponse:
    """Response from the Rekindle Brain"""
    strategy: str
    rationale: str
    action_plan: List[str]
    confidence_score: float
    training_signals: List[str]
    social_insights: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    generated_at: datetime

class RekindleBrain:
    """
    Main Rekindle Brain orchestration class.

    Coordinates all components: model management, training, inference,
    data pipelines, security, and agent integration.
    """

    def __init__(self, config: Optional[BrainConfig] = None):
        self.config = config or BrainConfig()
        self.model_manager = ModelManager(self.config)
        self.trainer = BrainTrainer(self.config)
        self.inference = BrainInference(self.config)
        self.data_pipeline = DataPipeline(self.config)
        self.security = SecurityManager(self.config)
        self.agent_integrator = AgentIntegrator(self.config)

        self.is_initialized = False
        self.deployment_type = DeploymentType.CPU  # Default to CPU

        logger.info("Rekindle Brain initialized")

    async def initialize(self, deployment_type: DeploymentType = DeploymentType.CPU) -> bool:
        """Initialize all brain components"""
        try:
            logger.info(f"Initializing Rekindle Brain for {deployment_type.value} deployment")

            self.deployment_type = deployment_type

            # Initialize components
            await self.model_manager.initialize(deployment_type)
            await self.data_pipeline.initialize()
            await self.security.initialize()
            await self.agent_integrator.initialize()

            # Load or download models
            await self.model_manager.load_base_models()

            # Initialize inference engine
            await self.inference.initialize(self.model_manager)

            self.is_initialized = True
            logger.info("Rekindle Brain initialization complete")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize Rekindle Brain: {e}")
            return False

    async def generate_business_strategy(self, query: Union[Dict[str, Any], BusinessQuery]) -> BrainResponse:
        """
        Generate a comprehensive business strategy.

        Main entry point for business intelligence queries.
        """
        if not self.is_initialized:
            raise RuntimeError("Rekindle Brain not initialized. Call initialize() first.")

        # Convert dict to BusinessQuery if needed
        if isinstance(query, dict):
            business_query = BusinessQuery(**query)
        else:
            business_query = query

        try:
            logger.info(f"Processing business strategy request: {business_query.goal[:50]}...")

            # Security check
            await self.security.validate_query(business_query)

            # Get agent insights
            agent_insights = await self.agent_integrator.gather_insights(business_query)

            # Retrieve relevant context from RAG
            context_data = await self.data_pipeline.retrieve_context(
                query=business_query.goal,
                task_type=business_query.task_type,
                filters={"social_intel": business_query.social_intel or []}
            )

            # Generate strategy using inference engine
            strategy_response = await self.inference.generate_strategy(
                query=business_query,
                context=context_data,
                agent_insights=agent_insights
            )

            # Create response
            response = BrainResponse(
                strategy=strategy_response.get("strategy", ""),
                rationale=strategy_response.get("rationale", ""),
                action_plan=strategy_response.get("action_plan", []),
                confidence_score=strategy_response.get("confidence_score", 0.0),
                training_signals=strategy_response.get("training_signals", []),
                social_insights=agent_insights.get("social_insights", []),
                metadata={
                    "model_used": strategy_response.get("model_used"),
                    "processing_time": strategy_response.get("processing_time"),
                    "tokens_used": strategy_response.get("tokens_used"),
                    "agent_contributions": list(agent_insights.keys())
                },
                generated_at=datetime.now()
            )

            # Store interaction for learning
            await self._store_interaction(business_query, response)

            logger.info(f"Generated business strategy with confidence {response.confidence_score:.2f}")

            return response

        except Exception as e:
            logger.error(f"Failed to generate business strategy: {e}")
            raise

    async def analyze_market_opportunity(self, data: Dict[str, Any], competitors: List[str],
                                       trends: List[str]) -> Dict[str, Any]:
        """Analyze market opportunities using social intelligence and business data"""
        query = BusinessQuery(
            task_type="market_analysis",
            goal=f"Analyze market opportunity with competitors: {', '.join(competitors[:3])}",
            context={"market_data": data, "competitors": competitors, "trends": trends},
            constraints={},
            social_intel=trends
        )

        response = await self.generate_business_strategy(query)

        return {
            "opportunity_score": response.confidence_score,
            "key_insights": response.action_plan,
            "competitive_advantages": response.social_insights,
            "recommended_strategy": response.strategy,
            "rationale": response.rationale
        }

    async def optimize_sales_sequence(self, current_sequence: List[str], outcomes: Dict[str, Any],
                                    objections: List[str]) -> Dict[str, Any]:
        """Optimize sales sequences based on performance data"""
        query = BusinessQuery(
            task_type="sales_optimization",
            goal="Optimize sales sequence for better conversion",
            context={
                "current_sequence": current_sequence,
                "performance_data": outcomes,
                "common_objections": objections
            },
            constraints={"max_sequence_length": 10},
            social_intel=["sales_best_practices", "objection_handling"]
        )

        response = await self.generate_business_strategy(query)

        return {
            "optimized_sequence": response.action_plan,
            "expected_improvement": f"{response.confidence_score * 100:.1f}%",
            "key_changes": response.training_signals,
            "rationale": response.rationale
        }

    async def negotiate_terms(self, proposal: Dict[str, Any], constraints: Dict[str, Any],
                            objectives: List[str]) -> Dict[str, Any]:
        """Provide negotiation strategies and counter-proposals"""
        query = BusinessQuery(
            task_type="negotiation",
            goal=f"Negotiate terms for: {proposal.get('deal_type', 'agreement')}",
            context={
                "proposal": proposal,
                "constraints": constraints,
                "objectives": objectives
            },
            constraints=constraints,
            social_intel=["negotiation_tactics", "deal_structuring"]
        )

        response = await self.generate_business_strategy(query)

        return {
            "negotiation_strategy": response.strategy,
            "counter_proposals": response.action_plan,
            "key_leverages": response.social_insights,
            "confidence": response.confidence_score,
            "rationale": response.rationale
        }

    async def fine_tune_on_business_data(self, data_path: str, model_type: ModelType = ModelType.MISTRAL_7B,
                                        output_dir: str = "models/fine_tuned") -> Dict[str, Any]:
        """Fine-tune the brain on proprietary business data"""
        logger.info(f"Starting fine-tuning on data from {data_path}")

        # Validate data security
        await self.security.validate_training_data(data_path)

        # Run training
        training_result = await self.trainer.fine_tune(
            model_type=model_type,
            data_path=data_path,
            output_dir=output_dir
        )

        # Update model manager with new model
        await self.model_manager.load_fine_tuned_model(training_result["model_path"])

        logger.info(f"Fine-tuning completed. New model loaded.")

        return training_result

    async def update_social_intelligence(self, social_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update RAG layer with fresh social intelligence"""
        logger.info(f"Updating social intelligence with {len(social_data)} items")

        # Process and store social data
        processed_data = await self.data_pipeline.process_social_data(social_data)

        # Update embeddings
        await self.data_pipeline.update_embeddings(processed_data)

        # Notify agents of new intelligence
        await self.agent_integrator.notify_social_update(processed_data)

        return {
            "items_processed": len(processed_data),
            "embeddings_updated": True,
            "agents_notified": True
        }

    async def evaluate_and_update(self, success_patterns: List[Dict[str, Any]],
                                failure_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use critic feedback to update model weights"""
        logger.info("Evaluating performance and updating model")

        # Get critic evaluation
        evaluation = await self.agent_integrator.get_critic_evaluation(
            success_patterns, failure_patterns
        )

        # Generate training signals
        training_signals = await self.trainer.generate_training_signals(evaluation)

        # Update model if significant improvements available
        if len(training_signals) > 10:  # Threshold for retraining
            logger.info(f"Retraining model with {len(training_signals)} new signals")

            # Create synthetic training data from signals
            synthetic_data = await self.trainer.create_synthetic_data(training_signals)

            # Fine-tune on new data
            await self.fine_tune_on_business_data(
                data_path=synthetic_data["data_path"],
                output_dir=f"models/auto_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

        return {
            "evaluation_complete": True,
            "training_signals_generated": len(training_signals),
            "model_updated": len(training_signals) > 10,
            "next_evaluation": "weekly"
        }

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "response_times": await self.inference.get_response_times(),
            "model_performance": await self.model_manager.get_model_metrics(),
            "data_freshness": await self.data_pipeline.get_data_freshness(),
            "agent_health": await self.agent_integrator.get_agent_health(),
            "security_status": await self.security.get_security_status()
        }

    async def _store_interaction(self, query: BusinessQuery, response: BrainResponse):
        """Store interaction for learning and analytics"""
        interaction_data = {
            "query": {
                "task_type": query.task_type,
                "goal": query.goal,
                "context_keys": list(query.context.keys()),
                "constraints": query.constraints,
                "social_intel_count": len(query.social_intel) if query.social_intel else 0
            },
            "response": {
                "confidence_score": response.confidence_score,
                "action_plan_length": len(response.action_plan),
                "training_signals": response.training_signals,
                "social_insights_count": len(response.social_insights)
            },
            "metadata": response.metadata,
            "timestamp": response.generated_at.isoformat()
        }

        # Store in data pipeline for future training
        await self.data_pipeline.store_interaction(interaction_data)

    async def shutdown(self):
        """Gracefully shutdown the brain"""
        logger.info("Shutting down Rekindle Brain")

        await self.inference.shutdown()
        await self.model_manager.shutdown()
        await self.data_pipeline.shutdown()
        await self.agent_integrator.shutdown()

        self.is_initialized = False
        logger.info("Rekindle Brain shutdown complete")

    def __str__(self) -> str:
        return f"RekindleBrain(deployment={self.deployment_type.value}, initialized={self.is_initialized})"

    def __repr__(self) -> str:
        return self.__str__()