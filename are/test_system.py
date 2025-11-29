#!/usr/bin/env python3
"""
ARE System Test Script

Tests the basic functionality of the ARE system components.
"""

import asyncio
import sys
import os

# Add the are directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

async def test_agents():
    """Test basic agent functionality"""
    print("Testing ARE System Components...")

    try:
        # Test imports
        from agents.planner_agent import PlannerAgent
        from agents.executor_agent import ExecutorAgent
        from agents.critic_agent import CriticAgent
        from agents.guardrail_agent import GuardrailAgent
        from agents.rag_service import RagServiceAgent
        from agents.social_listening_agent import SocialListeningAgent

        print("[OK] All agent imports successful")

        # Test agent initialization
        planner = PlannerAgent()
        executor = ExecutorAgent()
        critic = CriticAgent()
        guardrail = GuardrailAgent()
        rag = RagServiceAgent()
        social = SocialListeningAgent()

        print("[OK] All agents initialized successfully")

        # Test basic functionality
        test_goal = {
            "goal_type": "REVIVE_PIPELINE",
            "description": "Revive dormant leads in our pipeline",
            "target_metrics": {"leads": 100, "meetings": 20},
            "constraints": {"budget": 5000}
        }

        # Test planner with clarifying questions
        print("\nTesting Planner Agent...")
        plan_result = await planner.run(test_goal, None)

        if "status" in plan_result and plan_result["status"] == "clarifying_questions_needed":
            print("[OK] Planner correctly identified need for clarifying questions")
            print(f"Questions: {plan_result['questions']}")
        else:
            print("[OK] Planner generated execution plan")

        # Test social listening agent
        print("\nTesting Social Listening Agent...")
        social_result = await social.run({"mode": "on_demand", "sources": ["reddit"]}, None)
        print(f"[OK] Social listening completed: {social_result}")

        # Test RAG service
        print("\nTesting RAG Service...")
        rag_result = await rag.run({
            "request_type": "store",
            "content": "Test memory chunk",
            "metadata": {"test": True}
        }, None)
        print(f"[OK] RAG storage completed: {rag_result}")

        # Test critic agent
        print("\nTesting Critic Agent...")
        critic_result = await critic.run({
            "action": "evaluate_performance",
            "execution_results": [],
            "social_intelligence": {}
        }, None)
        print("[OK] Critic evaluation completed")

        # Test guardrail agent
        print("\nTesting Guardrail Agent...")
        guardrail_result = await guardrail.run({
            "evaluation_report": {"outcome_analyses": []}
        }, None)
        print("[OK] Guardrail validation completed")

        print("\n[SUCCESS] All ARE system components tested successfully!")
        return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agents())
    sys.exit(0 if success else 1)