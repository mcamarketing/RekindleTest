c#!/usr/bin/env python3
"""
Rekindle Brain Usage Examples

Demonstrates how to use the Rekindle Brain for business intelligence tasks.
"""

import asyncio
from rekindle_brain import RekindleBrain
from rekindle_brain.config import DeploymentType

async def main():
    """Main example demonstrating Rekindle Brain usage"""

    print("🤖 Initializing Rekindle Brain...")

    # Initialize brain (CPU deployment for development)
    brain = RekindleBrain()
    await brain.initialize(deployment_type=DeploymentType.CPU)

    print("✅ Brain initialized successfully")

    # Example 1: Business Strategy Generation
    print("\n📊 Example 1: Business Strategy Generation")
    strategy_result = await brain.generate_business_strategy({
        "task_type": "business_strategy",
        "goal": "Increase SaaS ARR by 30% in Q2",
        "context": {
            "company_size": "50 employees",
            "current_arr": "$2M",
            "target_market": "B2B tech companies"
        },
        "constraints": {
            "budget": 50000,
            "timeline": "3 months",
            "resources": "existing team"
        },
        "social_intel": ["pricing_trends", "competitor_moves"]
    })

    print(f"Strategy: {strategy_result.strategy}")
    print(f"Confidence: {strategy_result.confidence_score:.2f}")
    print(f"Action Plan: {strategy_result.action_plan}")

    # Example 2: Market Opportunity Analysis
    print("\n🎯 Example 2: Market Opportunity Analysis")
    market_analysis = await brain.analyze_market_opportunity(
        data={"market_size": "$50B", "growth_rate": "15%"},
        competitors=["CompetitorA", "CompetitorB", "CompetitorC"],
        trends=["AI adoption", "remote work", "cost optimization"]
    )

    print(f"Opportunity Score: {market_analysis['opportunity_score']:.2f}")
    print(f"Key Insights: {market_analysis['key_insights']}")

    # Example 3: Sales Sequence Optimization
    print("\n📈 Example 3: Sales Sequence Optimization")
    sequence_opt = await brain.optimize_sales_sequence(
        current_sequence=[
            "Initial email outreach",
            "Follow-up call",
            "Product demo",
            "Proposal delivery"
        ],
        outcomes={
            "reply_rate": 0.15,
            "meeting_conversion": 0.25,
            "close_rate": 0.12
        },
        objections=[
            "Budget constraints",
            "Current vendor satisfaction",
            "Timeline concerns"
        ]
    )

    print(f"Optimized Sequence: {sequence_opt['optimized_sequence']}")
    print(f"Expected Improvement: {sequence_opt['expected_improvement']}")

    # Example 4: Negotiation Strategy
    print("\n🤝 Example 4: Negotiation Strategy")
    negotiation = await brain.negotiate_terms(
        proposal={
            "deal_type": "SaaS subscription",
            "proposed_value": "$50K/year",
            "contract_length": "2 years"
        },
        constraints={
            "min_margin": 0.6,
            "max_discount": 0.15,
            "timeline": "end of quarter"
        },
        objectives=[
            "Maintain profitability",
            "Secure long-term commitment",
            "Create reference account"
        ]
    )

    print(f"Negotiation Strategy: {negotiation['negotiation_strategy']}")
    print(f"Counter Proposals: {negotiation['counter_proposals']}")

    # Get performance metrics
    print("\n📊 Performance Metrics")
    metrics = await brain.get_performance_metrics()
    print(f"Response Times: {metrics['response_times']}")
    print(f"Model Performance: {metrics['model_performance']}")

    # Cleanup
    await brain.shutdown()
    print("\n🧹 Brain shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())