#!/usr/bin/env python3
"""
ARE SDK Basic Usage Example

This example demonstrates the fundamental usage of the ARE SDK
for processing business goals and executing tasks.
"""

import asyncio
import os
from datetime import datetime

from are import (
    AREClient, AREConfig, Goal, GoalType, Priority,
    PlannerAgent, CriticAgent, RagServiceAgent
)


async def main():
    """Main example function"""
    print("🚀 ARE SDK Basic Usage Example")
    print("=" * 50)

    # Configuration
    config = AREConfig(
        base_url=os.getenv("ARE_BASE_URL", "http://localhost:8000"),
        api_key=os.getenv("ARE_API_KEY"),
        timeout=300,
        enable_streaming=True
    )

    # Initialize client
    async with AREClient(config) as client:
        print("✅ Connected to ARE system")

        # Example 1: Process a business goal
        print("\n📋 Example 1: Goal Processing")
        print("-" * 30)

        goal = Goal(
            goal_type=GoalType.INCREASE_MEETINGS,
            description="Increase qualified sales meetings by 30% this month through targeted outreach",
            target_metrics={
                "meetings": 45,
                "qualified_leads": 180,
                "response_rate": 0.25
            },
            constraints={
                "max_daily_emails": 100,
                "autonomy_level": "L2",  # Human approval for high-value actions
                "budget_limit": 2500
            },
            priority=Priority.HIGH,
            deadline=datetime(2024, 12, 31)
        )

        try:
            print(f"🎯 Processing goal: {goal.description}")
            plan = await client.process_goal(goal)

            print("✅ Goal processed successfully!"            print(f"📋 Plan ID: {plan.plan_id}")
            print(f"🎯 Goal: {plan.goal.description}")
            print(f"📊 Tasks: {len(plan.tasks)}")
            print(f"⚡ Estimated completion: {plan.estimated_completion}")
            print(f"🎲 Risk score: {plan.risk_assessment.get('score', 0):.2f}")

            # Show task breakdown
            print("\n📝 Execution Tasks:")
            for i, task in enumerate(plan.tasks[:3], 1):  # Show first 3 tasks
                print(f"  {i}. {task.description}")
                print(f"     Agent: {task.agent_type.value}")
                print(f"     Priority: {task.priority.value}")
                print(f"     Duration: {task.estimated_duration}s")

            if len(plan.tasks) > 3:
                print(f"  ... and {len(plan.tasks) - 3} more tasks")

        except Exception as e:
            print(f"❌ Goal processing failed: {e}")
            return

        # Example 2: Use specialized agent clients
        print("\n🤖 Example 2: Agent-Specific Operations")
        print("-" * 40)

        # Planner agent operations
        planner = PlannerAgent(client)
        try:
            print("🧠 Testing Planner Agent...")
            risks = await planner.assess_risks(goal, plan.tasks)
            print(f"🎲 Risk assessment: {risks.get('level', 'unknown')}")

        except Exception as e:
            print(f"⚠️ Planner agent test failed: {e}")

        # RAG Service operations
        rag = RagServiceAgent(client)
        try:
            print("🧠 Testing RAG Service...")

            # Store some context
            success = await rag.store_memory(
                key="campaign_strategy_q4",
                data={
                    "strategy": "Personalization-focused outreach",
                    "performance": 0.78,
                    "insights": ["Personalization increases response by 40%"]
                },
                tags=["campaign", "strategy", "personalization"]
            )

            if success:
                print("✅ Stored campaign context in memory")

                # Retrieve similar context
                results = await rag.search_memory(
                    "personalization strategy",
                    tags=["campaign"]
                )
                print(f"🔍 Found {len(results)} relevant memories")

        except Exception as e:
            print(f"⚠️ RAG service test failed: {e}")

        # Example 3: Real-time event handling
        print("\n📡 Example 3: Event Streaming")
        print("-" * 30)

        event_count = 0

        def handle_task_update(event):
            nonlocal event_count
            event_count += 1
            print(f"📡 Event {event_count}: {event.event_type} - {event.data.get('task_id', 'unknown')}")

        # Register event handler
        client.on_event("task_completed", handle_task_update)
        client.on_event("task_started", handle_task_update)

        try:
            print("🎧 Listening for events (10 seconds)...")
            await client.stream_events()

            # Wait for events
            await asyncio.sleep(10)

            print(f"📊 Received {event_count} events")

        except Exception as e:
            print(f"⚠️ Event streaming test failed: {e}")

        # Example 4: System health check
        print("\n🏥 Example 4: System Health")
        print("-" * 25)

        try:
            health = await client.health_check()
            print(f"💚 System status: {health['status']}")
            print(f"⏱️ Response time: {health.get('response_time', 'unknown')}ms")

            # Show agent statuses
            metrics = client.get_metrics()
            print(f"📊 Agents monitored: {len(metrics)}")

            for agent_type, agent_metrics in metrics.items():
                success_rate = (agent_metrics.requests_successful /
                              max(agent_metrics.requests_total, 1)) * 100
                print(f"  {agent_type.value}: {success_rate:.1f}% success rate")

        except Exception as e:
            print(f"⚠️ Health check failed: {e}")

    print("\n🎉 ARE SDK example completed!")
    print("\n💡 Next steps:")
    print("  • Explore more examples in examples/")
    print("  • Check the full API documentation")
    print("  • Integrate ARE agents into your application")


if __name__ == "__main__":
    # Set up basic logging
    import logging
    logging.basicConfig(level=logging.INFO)

    # Run the example
    asyncio.run(main())