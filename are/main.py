"""
ARE (Autonomous Revenue Engine) - Main Entry Point

This module provides the main entry point for the ARE system,
including initialization, goal processing, and system orchestration.
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any, Optional
from datetime import datetime

from .orchestration.dag_engine import DAGEngine
from .agents.planner_agent import PlannerAgent
from .agents.executor_agent import ExecutorAgent
from .agents.critic_agent import CriticAgent
from .agents.guardrail_agent import GuardrailAgent
from .agents.rag_service import RagServiceAgent
from .agents.social_listening_agent import SocialListeningAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('are.log')
    ]
)

logger = logging.getLogger(__name__)

class ARESystem:
    """Main ARE System orchestrator"""

    def __init__(self):
        self.dag_engine = None
        self.planner = None
        self.executor = None
        self.critic = None
        self.guardrail = None
        self.rag_service = None
        self.social_listening = None
        self.is_running = False

    async def initialize(self):
        """Initialize the ARE system"""
        logger.info("Initializing ARE (Autonomous Revenue Engine)...")

        try:
            # Initialize DAG engine
            self.dag_engine = DAGEngine()

            # Load orchestration graph
            await self.dag_engine.load_graph()

            # Initialize core agents
            self.planner = PlannerAgent()
            self.executor = ExecutorAgent()
            self.critic = CriticAgent()
            self.guardrail = GuardrailAgent()
            self.rag_service = RagServiceAgent()
            self.social_listening = SocialListeningAgent()

            logger.info("ARE system initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize ARE system: {e}")
            return False

    async def process_goal(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Process a user goal through the ARE system"""
        if not self.dag_engine:
            raise RuntimeError("ARE system not initialized")

        logger.info(f"Processing goal: {goal.get('description', 'Unknown')}")

        try:
            # Execute goal through DAG engine
            result = await self.dag_engine.execute_goal(goal)

            logger.info(f"Goal processing completed: {result.get('status', 'unknown')}")
            return result

        except Exception as e:
            logger.error(f"Goal processing failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        status = {
            "is_running": self.is_running,
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }

        if self.dag_engine:
            status["components"]["dag_engine"] = self.dag_engine.get_health()

        if self.planner:
            status["components"]["planner"] = {"status": "ready"}

        if self.executor:
            status["components"]["executor"] = {"status": "ready"}

        if self.critic:
            status["components"]["critic"] = await self.critic.get_learning_insights()

        if self.guardrail:
            status["components"]["guardrail"] = await self.guardrail.get_risk_summary()

        if self.rag_service:
            status["components"]["rag_service"] = await self.rag_service.get_memory_stats()

        if self.social_listening:
            status["components"]["social_listening"] = await self.social_listening.get_intelligence_summary()

        return status

    async def shutdown(self):
        """Gracefully shutdown the ARE system"""
        logger.info("Shutting down ARE system...")

        self.is_running = False

        if self.dag_engine:
            await self.dag_engine.shutdown()

        if self.social_listening:
            await self.social_listening.stop()

        logger.info("ARE system shutdown complete")

# Global ARE system instance
are_system = ARESystem()

async def handle_goal(goal_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a goal processing request"""
    return await are_system.process_goal(goal_data)

async def get_status() -> Dict[str, Any]:
    """Get system status"""
    return await are_system.get_system_status()

async def main():
    """Main entry point for ARE system"""
    logger.info("Starting ARE (Autonomous Revenue Engine)")

    # Initialize system
    if not await are_system.initialize():
        logger.error("Failed to initialize ARE system")
        return 1

    are_system.is_running = True

    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(are_system.shutdown())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        logger.info("ARE system is running and ready to process goals")
        logger.info("Use handle_goal() to process revenue goals")

        # Keep the system running
        while are_system.is_running:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"ARE system error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    # Run the ARE system
    exit_code = asyncio.run(main())
    sys.exit(exit_code)