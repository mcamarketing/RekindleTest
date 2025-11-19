"""Simple test without Unicode"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("Testing Special Forces Crews...")
print("-" * 40)

try:
    from crewai_agents.crews.special_forces_crews import SpecialForcesCoordinator
    print("[OK] Import successful")

    coordinator = SpecialForcesCoordinator()
    print("[OK] Coordinator initialized")

    crews = list(coordinator.crews.keys())
    print(f"[OK] {len(crews)} crews found: {crews}")

    # Test Crew A structure
    crew_a = coordinator.crews["lead_reactivation"]
    agents_a = list(crew_a.agents.keys())
    print(f"[OK] Crew A has {len(agents_a)} agents: {agents_a}")

    # Test Crew B structure
    crew_b = coordinator.crews["engagement_followups"]
    agents_b = list(crew_b.agents.keys())
    print(f"[OK] Crew B has {len(agents_b)} agents: {agents_b}")

    # Test Crew C structure
    crew_c = coordinator.crews["revenue_conversion"]
    agents_c = list(crew_c.agents.keys())
    print(f"[OK] Crew C has {len(agents_c)} agents: {agents_c}")

    # Test Crew D structure
    crew_d = coordinator.crews["optimization_intelligence"]
    agents_d = list(crew_d.agents.keys())
    print(f"[OK] Crew D has {len(agents_d)} agents: {agents_d}")

    print("-" * 40)
    print("All tests passed!")

except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
