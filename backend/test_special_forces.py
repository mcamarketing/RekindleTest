"""
Test Special Forces Crew System
Quick validation without pytest
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from crewai_agents.crews.special_forces_crews import (
            LeadReactivationCrew,
            EngagementFollowUpsCrew,
            RevenueConversionCrew,
            OptimizationIntelligenceCrew,
            SpecialForcesCoordinator
        )
        print("[OK] All crew imports successful")
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crew_initialization():
    """Test that crews can be initialized"""
    print("\nTesting crew initialization...")
    try:
        from crewai_agents.crews.special_forces_crews import SpecialForcesCoordinator

        coordinator = SpecialForcesCoordinator()
        print(f"✓ SpecialForcesCoordinator initialized")

        # Check that all 4 crews are initialized
        assert "lead_reactivation" in coordinator.crews
        assert "engagement_followups" in coordinator.crews
        assert "revenue_conversion" in coordinator.crews
        assert "optimization_intelligence" in coordinator.crews
        print(f"✓ All 4 crews initialized: {list(coordinator.crews.keys())}")

        return True
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crew_structure():
    """Test that each crew has correct sub-agents"""
    print("\nTesting crew structure...")
    try:
        from crewai_agents.crews.special_forces_crews import (
            LeadReactivationCrew,
            EngagementFollowUpsCrew,
            RevenueConversionCrew,
            OptimizationIntelligenceCrew
        )

        # Test Crew A
        crew_a = LeadReactivationCrew()
        assert "scorer" in crew_a.agents
        assert "researcher" in crew_a.agents
        assert "msg_gen" in crew_a.agents
        assert "compliance" in crew_a.agents
        assert "scheduler" in crew_a.agents
        print(f"✓ Crew A (Lead Reactivation) has 5 sub-agents: {list(crew_a.agents.keys())}")

        # Test Crew B
        crew_b = EngagementFollowUpsCrew()
        assert "tracker" in crew_b.agents
        assert "followup" in crew_b.agents
        assert "ab_tester" in crew_b.agents
        assert "analyzer" in crew_b.agents
        print(f"✓ Crew B (Engagement & Follow-Ups) has 4 sub-agents: {list(crew_b.agents.keys())}")

        # Test Crew C
        crew_c = RevenueConversionCrew()
        assert "booker" in crew_c.agents
        assert "billing" in crew_c.agents
        assert "upsell" in crew_c.agents
        assert "conv_analyzer" in crew_c.agents
        print(f"✓ Crew C (Revenue & Conversion) has 4 sub-agents: {list(crew_c.agents.keys())}")

        # Test Crew D
        crew_d = OptimizationIntelligenceCrew()
        assert "ab_designer" in crew_d.agents
        assert "competitor" in crew_d.agents
        assert "personalizer" in crew_d.agents
        assert "data_analyst" in crew_d.agents
        print(f"✓ Crew D (Optimization & Intelligence) has 4 sub-agents: {list(crew_d.agents.keys())}")

        return True
    except Exception as e:
        print(f"✗ Structure error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rex_integration():
    """Test that REX can access Special Forces"""
    print("\nTesting REX integration...")
    try:
        from crewai_agents.agents.rex.rex import RexOrchestrator

        # Initialize REX without user_id (testing mode)
        rex = RexOrchestrator(user_id=None)

        # Check that special_forces is initialized
        assert hasattr(rex, 'special_forces')
        assert rex.special_forces is not None
        print("✓ REX has special_forces coordinator")

        # Check that action_executor has special_forces
        assert hasattr(rex.action_executor, 'special_forces')
        assert rex.action_executor.special_forces is not None
        print("✓ ActionExecutor has special_forces coordinator")

        # Check feature flag
        assert hasattr(rex.action_executor, 'use_special_forces')
        print(f"✓ use_special_forces flag: {rex.action_executor.use_special_forces}")

        return True
    except Exception as e:
        print(f"✗ REX integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint_import():
    """Test that API endpoint can import Special Forces"""
    print("\nTesting API endpoint import...")
    try:
        # Simulate the import from api_server.py
        from crewai_agents.crews.special_forces_crews import SpecialForcesCoordinator

        special_forces = SpecialForcesCoordinator()
        print("✓ API can import and instantiate SpecialForcesCoordinator")

        # Test that coordinator methods exist
        assert hasattr(special_forces, 'run_campaign')
        assert hasattr(special_forces, 'track_engagement')
        assert hasattr(special_forces, 'optimize_revenue')
        assert hasattr(special_forces, 'run_optimization')
        print("✓ All coordinator methods exist")

        return True
    except Exception as e:
        print(f"✗ API import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("SPECIAL FORCES CREW SYSTEM - VALIDATION TESTS")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Crew Initialization", test_crew_initialization),
        ("Crew Structure", test_crew_structure),
        ("REX Integration", test_rex_integration),
        ("API Endpoint Import", test_api_endpoint_import)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Special Forces Crew system is operational.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
