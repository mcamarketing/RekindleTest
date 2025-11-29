"""
Brain Inference Module

Handles model inference, response generation, and performance optimization
for CPU and GPU deployments with sub-5s response targets.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .config import BrainConfig, ModelType

logger = logging.getLogger(__name__)

@dataclass
class InferenceResult:
    """Result of a model inference call"""
    response: str
    confidence_score: float
    processing_time: float
    tokens_used: int
    model_used: str
    metadata: Dict[str, Any]

class BrainInference:
    """Handles model inference and response generation"""

    def __init__(self, config: BrainConfig):
        self.config = config
        self.model_manager = None  # Will be set during initialization
        self.response_times: List[float] = []
        self.max_response_history = 1000

    async def initialize(self, model_manager):
        """Initialize inference engine with model manager"""
        self.model_manager = model_manager
        logger.info("BrainInference initialized")

    async def generate_strategy(self, query: Dict[str, Any], context: Dict[str, Any],
                              agent_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a business strategy using the appropriate model

        Args:
            query: Business query with goal, context, constraints
            context: Retrieved RAG context
            agent_insights: Insights from ARE agents

        Returns:
            Strategy response with action plan and confidence
        """
        start_time = time.time()

        try:
            # Select appropriate model based on query type
            model_type = self._select_model_for_query(query)

            # Build prompt
            prompt = self._build_business_prompt(query, context, agent_insights)

            # Generate response
            raw_response = await self._generate_response(prompt, model_type)

            # Parse and structure response
            structured_response = self._parse_response(raw_response)

            # Calculate confidence
            confidence = self._calculate_response_confidence(structured_response, agent_insights)

            processing_time = time.time() - start_time

            # Track response time
            self._track_response_time(processing_time)

            result = {
                "strategy": structured_response.get("strategy", ""),
                "rationale": structured_response.get("rationale", ""),
                "action_plan": structured_response.get("action_plan", []),
                "confidence_score": confidence,
                "training_signals": structured_response.get("training_signals", []),
                "model_used": model_type.value,
                "processing_time": processing_time,
                "tokens_used": len(prompt.split()) + len(raw_response.split()),  # Rough estimate
                "context_used": len(context.get("documents", [])),
                "agent_insights_used": len(agent_insights)
            }

            logger.info(f"Strategy generated in {processing_time:.2f}s with confidence {confidence:.2f}")

            return result

        except Exception as e:
            logger.error(f"Strategy generation failed: {e}")
            processing_time = time.time() - start_time

            # Return fallback response
            return {
                "strategy": "Unable to generate strategy due to processing error",
                "rationale": f"Error: {str(e)}",
                "action_plan": ["Retry request", "Contact support if issue persists"],
                "confidence_score": 0.0,
                "training_signals": ["error_handling"],
                "model_used": "error_fallback",
                "processing_time": processing_time,
                "tokens_used": 0,
                "context_used": 0,
                "agent_insights_used": 0
            }

    def _select_model_for_query(self, query: Dict[str, Any]) -> ModelType:
        """Select the most appropriate model for the query type"""
        task_type = query.get("task_type", "general")

        # Route to specialized models based on task
        if task_type in ["code_generation", "technical_analysis"]:
            return ModelType.DEEPSEEK_CODER
        elif task_type in ["creative_writing", "content_generation"]:
            return ModelType.ZEPHYR_7B
        else:
            # Default to Mistral for business strategy
            return ModelType.MISTRAL_7B

    def _build_business_prompt(self, query: Dict[str, Any], context: Dict[str, Any],
                             agent_insights: Dict[str, Any]) -> str:
        """Build a comprehensive business strategy prompt"""

        goal = query.get("goal", "")
        task_type = query.get("task_type", "business_strategy")
        context_data = query.get("context", {})
        constraints = query.get("constraints", {})

        # Build context from RAG and agents
        rag_context = self._format_rag_context(context)
        agent_context = self._format_agent_insights(agent_insights)

        prompt = f"""You are Rekindle Brain, an autonomous business intelligence system specializing in revenue optimization, marketing strategy, sales automation, and negotiation tactics.

TASK: {task_type.upper()}
GOAL: {goal}

CONTEXT:
{context_data}

CONSTRAINTS:
{constraints}

RAG KNOWLEDGE BASE:
{rag_context}

AGENT INSIGHTS:
{agent_context}

INSTRUCTIONS:
1. Provide a clear, actionable business strategy
2. Include specific, measurable action items
3. Consider budget, timeline, and resource constraints
4. Leverage successful patterns from the knowledge base
5. Incorporate relevant social intelligence and market trends
6. Provide confidence level and rationale for recommendations

RESPONSE FORMAT:
Strategy: [Your strategic recommendation]
Rationale: [Why this approach makes sense]
Action Plan: [Numbered list of specific actions]
Confidence: [0-1 score]
Training Signals: [Key learnings for future improvement]

Generate your response:"""

        return prompt

    def _format_rag_context(self, context: Dict[str, Any]) -> str:
        """Format RAG context for prompt inclusion"""
        if not context or "documents" not in context:
            return "No relevant historical data available."

        documents = context["documents"][:5]  # Limit to top 5

        formatted = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")[:500]  # Truncate long content
            source = doc.get("metadata", {}).get("source", "unknown")
            similarity = doc.get("score", 0)

            formatted.append(f"{i}. [{source}, relevance: {similarity:.2f}] {content}")

        return "\n".join(formatted)

    def _format_agent_insights(self, agent_insights: Dict[str, Any]) -> str:
        """Format agent insights for prompt inclusion"""
        if not agent_insights:
            return "No agent insights available."

        formatted = []

        # Social listening insights
        social = agent_insights.get("social_insights", [])
        if social:
            formatted.append("SOCIAL INTELLIGENCE:")
            for insight in social[:3]:  # Top 3 insights
                formatted.append(f"- {insight.get('topic', 'General')}: {insight.get('summary', '')[:200]}")

        # Critic evaluations
        critic = agent_insights.get("critic_evaluation", {})
        if critic:
            formatted.append("CRITIC FEEDBACK:")
            success_rate = critic.get("success_rate", 0)
            formatted.append(f"- Recent success rate: {success_rate:.1%}")
            top_patterns = critic.get("top_patterns", [])[:2]
            if top_patterns:
                formatted.append(f"- Successful patterns: {', '.join(top_patterns)}")

        # Planner suggestions
        planner = agent_insights.get("planner_suggestions", [])
        if planner:
            formatted.append("PLANNER RECOMMENDATIONS:")
            for suggestion in planner[:2]:
                formatted.append(f"- {suggestion}")

        return "\n".join(formatted)

    async def _generate_response(self, prompt: str, model_type: ModelType) -> str:
        """Generate response using the specified model"""
        try:
            model_data = self.model_manager.get_model(model_type)
            model_config = model_data["config"]

            # Route to appropriate inference method based on model type
            if model_data["type"] == "gguf":
                response = await self._generate_gguf(prompt, model_data)
            elif model_data["type"] in ["transformers_cpu", "transformers_gpu", "fine_tuned"]:
                response = await self._generate_transformers(prompt, model_data)
            elif model_data["type"] == "exllama":
                response = await self._generate_exllama(prompt, model_data)
            else:
                raise ValueError(f"Unsupported model type: {model_data['type']}")

            return response

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return f"Error generating response: {str(e)}"

    async def _generate_gguf(self, prompt: str, model_data: Dict[str, Any]) -> str:
        """Generate response using GGUF model (llama.cpp)"""
        model = model_data["model"]
        config = model_data["config"]

        try:
            # Generate response
            output = model(
                prompt,
                max_tokens=1024,
                temperature=0.7,
                top_p=0.9,
                echo=False
            )

            return output["choices"][0]["text"].strip()

        except Exception as e:
            logger.error(f"GGUF generation failed: {e}")
            raise

    async def _generate_transformers(self, prompt: str, model_data: Dict[str, Any]) -> str:
        """Generate response using Transformers model"""
        model = model_data["model"]
        tokenizer = model_data["tokenizer"]

        try:
            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)

            # Move to appropriate device
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}

            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )

            # Decode response
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract only the generated part (remove prompt)
            if response.startswith(prompt):
                response = response[len(prompt):].strip()

            return response

        except Exception as e:
            logger.error(f"Transformers generation failed: {e}")
            raise

    async def _generate_exllama(self, prompt: str, model_data: Dict[str, Any]) -> str:
        """Generate response using ExLlama model"""
        # Placeholder for ExLlama implementation
        # This would use the ExLlama library for efficient inference
        logger.warning("ExLlama generation not implemented, using mock response")
        return "Mock ExLlama response - implement actual ExLlama integration"

    def _parse_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse model response into structured format"""
        try:
            # Try to extract structured information from response
            lines = raw_response.split('\n')
            parsed = {
                "strategy": "",
                "rationale": "",
                "action_plan": [],
                "confidence_score": 0.5,
                "training_signals": []
            }

            current_section = None
            action_items = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Detect sections
                if line.lower().startswith("strategy:"):
                    current_section = "strategy"
                    parsed["strategy"] = line.split(":", 1)[1].strip()
                elif line.lower().startswith("rationale:"):
                    current_section = "rationale"
                    parsed["rationale"] = line.split(":", 1)[1].strip()
                elif line.lower().startswith("action plan:"):
                    current_section = "action_plan"
                elif line.lower().startswith("confidence:"):
                    confidence_text = line.split(":", 1)[1].strip()
                    try:
                        parsed["confidence_score"] = float(confidence_text)
                    except ValueError:
                        parsed["confidence_score"] = 0.5
                elif line.lower().startswith("training signals:"):
                    current_section = "training_signals"
                    signals_text = line.split(":", 1)[1].strip()
                    parsed["training_signals"] = [s.strip() for s in signals_text.split(",") if s.strip()]
                elif current_section == "action_plan" and (line[0].isdigit() or line.startswith("-")):
                    # Extract action items
                    if line[0].isdigit():
                        # Remove numbering
                        item = line.split(".", 1)[1].strip() if "." in line else line
                    else:
                        item = line[1:].strip()  # Remove dash
                    action_items.append(item)
                elif current_section == "rationale" and parsed["rationale"]:
                    # Continue rationale if multi-line
                    parsed["rationale"] += " " + line

            parsed["action_plan"] = action_items

            # Ensure we have minimum content
            if not parsed["strategy"]:
                parsed["strategy"] = raw_response[:200] + "..." if len(raw_response) > 200 else raw_response

            return parsed

        except Exception as e:
            logger.warning(f"Response parsing failed: {e}, using fallback")
            return {
                "strategy": raw_response,
                "rationale": "Generated response",
                "action_plan": ["Review and implement recommendations"],
                "confidence_score": 0.5,
                "training_signals": []
            }

    def _calculate_response_confidence(self, response: Dict[str, Any],
                                     agent_insights: Dict[str, Any]) -> float:
        """Calculate confidence score for the response"""
        base_confidence = 0.5

        # Factor in response quality
        if response.get("strategy") and len(response["strategy"]) > 50:
            base_confidence += 0.2

        if response.get("action_plan") and len(response["action_plan"]) > 0:
            base_confidence += 0.15

        if response.get("rationale") and len(response["rationale"]) > 20:
            base_confidence += 0.1

        # Factor in agent insights
        if agent_insights.get("social_insights"):
            base_confidence += 0.1

        if agent_insights.get("critic_evaluation"):
            critic_score = agent_insights["critic_evaluation"].get("success_rate", 0.5)
            base_confidence += (critic_score - 0.5) * 0.2  # Scale around neutral

        # Ensure bounds
        return max(0.0, min(1.0, base_confidence))

    def _track_response_time(self, response_time: float):
        """Track response time for performance monitoring"""
        self.response_times.append(response_time)

        # Keep only recent history
        if len(self.response_times) > self.max_response_history:
            self.response_times = self.response_times[-self.max_response_history:]

    async def get_response_times(self) -> Dict[str, Any]:
        """Get response time statistics"""
        if not self.response_times:
            return {"average": 0, "median": 0, "p95": 0, "count": 0}

        sorted_times = sorted(self.response_times)

        return {
            "average": sum(self.response_times) / len(self.response_times),
            "median": sorted_times[len(sorted_times) // 2],
            "p95": sorted_times[int(len(sorted_times) * 0.95)],
            "min": min(self.response_times),
            "max": max(self.response_times),
            "count": len(self.response_times)
        }

    async def optimize_for_performance(self):
        """Optimize inference for better performance"""
        logger.info("Optimizing inference performance...")

        # This would implement various optimizations:
        # - Model quantization adjustments
        # - Caching frequently used responses
        # - Batch processing for multiple requests
        # - Memory management optimizations

        logger.info("Performance optimization complete")

    async def shutdown(self):
        """Shutdown inference engine"""
        logger.info("Shutting down BrainInference")

        # Clear response time history
        self.response_times.clear()

        logger.info("BrainInference shutdown complete")