#!/usr/bin/env python3
"""
Basic structure test for ARE system
Tests imports and basic functionality without external dependencies
"""

import sys
import os

# Add the are directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported"""
    try:
        # Test agent imports
        from agents.planner_agent import PlannerAgent
        from agents.executor_agent import ExecutorAgent
        from agents.critic_agent import CriticAgent
        from agents.guardrail_agent import GuardrailAgent
        from agents.rag_service import RagServiceAgent
        from agents.social_listening_agent import SocialListeningAgent

        # Test wrapper imports
        from integrations.rex_wrappers.rex_state import RexStateAgent
        from integrations.rex_wrappers.rex_analytics import RexAnalyticsAgent
        from integrations.rex_wrappers.rex_decision import RexDecisionAgent
        from integrations.rex_wrappers.rex_scheduler import RexSchedulerAgent

        from integrations.services_wrappers.revenue_forecaster import RevenueForecasterAgent
        from integrations.services_wrappers.icp_generator import ICPGeneratorAgent

        print("[PASS] All imports successful")
        return True

    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_agent_instantiation():
    """Test that agents can be instantiated"""
    try:
        from agents.social_listening_agent import SocialListeningAgent
        from agents.planner_agent import PlannerAgent

        # Test SocialListeningAgent
        social_agent = SocialListeningAgent()
        print("[PASS] SocialListeningAgent instantiated")

        # Test PlannerAgent
        planner_agent = PlannerAgent()
        print("[PASS] PlannerAgent instantiated")

        return True

    except Exception as e:
        print(f"✗ Agent instantiation failed: {e}")
        return False

def test_basic_functionality():
    """Test basic agent functionality"""
    try:
        from agents.social_listening_agent import SocialListeningAgent

        agent = SocialListeningAgent()

        # Test mock data generation
        mock_reddit = agent._get_mock_reddit_posts("test")
        print(f"[PASS] Mock Reddit data generated: {len(mock_reddit)} posts")

        mock_forum = agent._get_mock_forum_posts()
        print(f"[PASS] Mock forum data generated: {len(mock_forum)} posts")

        return True

    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("ARE System Basic Structure Test")
    print("=" * 40)

    tests = [
        ("Import Test", test_imports),
        ("Instantiation Test", test_agent_instantiation),
        ("Basic Functionality Test", test_basic_functionality)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  Failed: {test_name}")

    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] All tests passed! ARE system structure is valid.")
        return 0
    else:
        print("[FAILURE] Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())