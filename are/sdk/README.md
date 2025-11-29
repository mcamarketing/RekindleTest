# ARE SDK - Autonomous Revenue Engine Software Development Kit

The ARE SDK provides programmatic access to all ARE (Autonomous Revenue Engine) agents and services, enabling any part of the Rekindle platform to leverage AI capabilities.

## 🚀 Quick Start

```python
import asyncio
from are import AREClient, Goal, GoalType, Priority

async def main():
    # Initialize client
    client = AREClient()

    async with client:
        # Create a business goal
        goal = Goal(
            goal_type=GoalType.INCREASE_MEETINGS,
            description="Increase qualified meetings by 25% this quarter",
            target_metrics={"meetings": 50, "qualified_leads": 200},
            priority=Priority.HIGH
        )

        # Process the goal
        plan = await client.process_goal(goal)
        print(f"Created plan with {len(plan.tasks)} tasks")

        # Execute tasks
        for task in plan.tasks:
            result = await client.execute_task(task)
            print(f"Task {task.id}: {result.success}")

asyncio.run(main())
```

## 📦 Installation

```bash
# From Rekindle workspace
pip install -e ./are/sdk

# Or add to requirements.txt
-e ./are/sdk
```

## 🏗️ Architecture

### Core Components

- **`AREClient`**: Main client for ARE system interaction
- **Agent Clients**: Specialized clients for each agent type
- **Communication Layer**: HTTP/WebSocket communication with retry logic
- **Type System**: Comprehensive type definitions and validation

### Agent Types

| Agent | Purpose | Key Capabilities |
|-------|---------|------------------|
| **Planner** | Goal decomposition & planning | Task creation, risk assessment, prioritization |
| **Executor** | Task execution & routing | Agent coordination, progress tracking, error handling |
| **Critic** | Performance evaluation | Quality assessment, insight generation, outcome evaluation |
| **Guardrail** | Safety & compliance | Content validation, permissions, rate limiting |
| **RAG Service** | Memory & context | Knowledge retrieval, memory storage, semantic search |
| **Social Listening** | Market intelligence | Sentiment analysis, trend detection, insight extraction |

## 📋 API Reference

### AREClient

#### Initialization

```python
from are import AREClient, AREConfig

# Basic configuration
client = AREClient()

# Advanced configuration
config = AREConfig(
    base_url="https://are.rekindle.ai",
    websocket_url="wss://are.rekindle.ai/stream",
    api_key="your-api-key",
    timeout=300,
    org_id="org_123",
    user_id="user_456"
)
client = AREClient(config)
```

#### Goal Processing

```python
from are import Goal, GoalType, Priority

goal = Goal(
    goal_type=GoalType.REVIVE_PIPELINE,
    description="Reactivate dormant leads from Q1",
    target_metrics={"reactivations": 100, "meetings": 15},
    constraints={"max_budget": 5000},
    priority=Priority.HIGH
)

plan = await client.process_goal(goal)
print(f"Plan ID: {plan.plan_id}")
print(f"Estimated completion: {plan.estimated_completion}")
```

#### Task Execution

```python
from are import Task, AgentType

task = Task(
    id="task_001",
    description="Research high-value dormant leads",
    agent_type=AgentType.CREWAI,
    capabilities=["lead_research", "data_analysis"],
    input_data={"segment": "dormant_30_days", "min_value": 50000}
)

result = await client.execute_task(task)
if result.success:
    print(f"Found {len(result.result['leads'])} leads")
else:
    print(f"Task failed: {result.error}")
```

#### Event Streaming

```python
# Subscribe to real-time events
await client.stream_events(["task_completed", "goal_achieved"])

# Handle events
def handle_task_completion(event):
    print(f"Task {event.data['task_id']} completed")

client.on_event("task_completed", handle_task_completion)
```

### Agent-Specific Clients

#### Planner Agent

```python
from are import PlannerAgent

planner = PlannerAgent(client)

# Create detailed execution plan
plan_details = await planner.create_plan(goal)

# Decompose goal into tasks
tasks = await planner.decompose_goal(goal)

# Assess execution risks
risks = await planner.assess_risks(goal, tasks)
```

#### Critic Agent

```python
from are import CriticAgent

critic = CriticAgent(client)

# Evaluate agent performance
performance = await critic.evaluate_performance(agent_responses)

# Generate insights
insights = await critic.generate_insights(execution_data)

# Assess goal achievement
assessment = await critic.assess_outcomes(goal, results)
```

#### RAG Service Agent

```python
from are import RagServiceAgent

rag = RagServiceAgent(client)

# Retrieve relevant context
context = await rag.retrieve_context("customer pain points in SaaS")

# Store new information
success = await rag.store_memory(
    key="campaign_2024_q1",
    data={"performance": 0.85, "insights": ["..."]},
    tags=["campaign", "q1", "performance"]
)

# Search memory
results = await rag.search_memory("campaign performance", tags=["2024"])
```

#### Social Listening Agent

```python
from are import SocialListeningAgent

social = SocialListeningAgent(client)

# Collect market intelligence
intelligence = await social.collect_intelligence(
    sources=["reddit", "forums"],
    topics=["customer support", "pricing"]
)

# Analyze sentiment
sentiment = await social.analyze_sentiment("This product is amazing!")

# Get intelligence summary
summary = await social.get_intelligence_summary("last_week")
```

## 🔧 Advanced Usage

### Custom Configuration

```python
config = AREConfig(
    base_url="https://staging-are.rekindle.ai",
    api_key=os.getenv("ARE_API_KEY"),
    timeout=600,  # 10 minutes for complex goals
    retry_attempts=5,
    enable_streaming=True,
    org_id="org_12345"
)
```

### Error Handling

```python
from are import AREError, TimeoutError, AgentUnavailableError

try:
    result = await client.process_goal(goal)
except TimeoutError as e:
    print(f"Goal processing timed out: {e}")
    # Implement fallback logic
except AgentUnavailableError as e:
    print(f"Agent {e.agent_type} unavailable: {e}")
    # Try alternative agent or queue for later
except AREError as e:
    print(f"ARE error: {e}")
    # Log and handle appropriately
```

### Event-Driven Architecture

```python
# Set up event handlers
async def on_goal_completed(event):
    goal_id = event.data['goal_id']
    print(f"Goal {goal_id} completed successfully!")

async def on_task_failed(event):
    task_id = event.data['task_id']
    error = event.data['error']
    print(f"Task {task_id} failed: {error}")
    # Implement retry logic or notifications

client.on_event("goal_completed", on_goal_completed)
client.on_event("task_failed", on_task_failed)

# Start streaming
await client.stream_events()
```

### Batch Operations

```python
# Process multiple goals concurrently
goals = [goal1, goal2, goal3]

plans = await asyncio.gather(*[
    client.process_goal(goal) for goal in goals
])

# Execute tasks in parallel with concurrency control
semaphore = asyncio.Semaphore(5)  # Max 5 concurrent tasks

async def execute_with_limit(task):
    async with semaphore:
        return await client.execute_task(task)

results = await asyncio.gather(*[
    execute_with_limit(task) for task in tasks
])
```

## 🔒 Security & Compliance

### Authentication
- API key-based authentication
- Organization and user context isolation
- Request signing for sensitive operations

### Permissions
```python
# Check permissions before operations
allowed = await guardrail.check_permissions(
    action="process_goal",
    resource="revenue_goals",
    user_id="user_123"
)

if allowed:
    plan = await client.process_goal(goal)
```

### Rate Limiting
- Automatic rate limit detection and handling
- Exponential backoff for retries
- Configurable limits per organization

## 📊 Monitoring & Metrics

### Client Metrics
```python
# Get client performance metrics
metrics = client.get_metrics()

for agent_type, agent_metrics in metrics.items():
    print(f"{agent_type.value}: {agent_metrics.requests_successful}/{agent_metrics.requests_total} successful")
```

### Health Checks
```python
# System health check
health = await client.health_check()
if health['status'] == 'healthy':
    print("ARE system is operational")
else:
    print(f"System issues: {health['error']}")
```

## 🧪 Testing

### Mock Client for Testing
```python
from are.testing import MockAREClient

# Use mock client for unit tests
mock_client = MockAREClient()
mock_client.mock_response("process_goal", mock_plan)

plan = await mock_client.process_goal(goal)
assert plan.plan_id == "mock_plan_123"
```

### Integration Testing
```python
import pytest

@pytest.mark.asyncio
async def test_goal_processing():
    async with AREClient(test_config) as client:
        goal = create_test_goal()
        plan = await client.process_goal(goal)

        assert len(plan.tasks) > 0
        assert plan.estimated_completion > datetime.now()
```

## 🚀 Production Deployment

### Docker Integration
```dockerfile
FROM python:3.11-slim

COPY are/sdk/ /app/are/sdk/
RUN pip install -e /app/are/sdk

# Your application code
COPY . /app
RUN pip install -r requirements.txt

CMD ["python", "your_app.py"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rekindle-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: rekindle/app:latest
        env:
        - name: ARE_BASE_URL
          value: "https://are.rekindle.ai"
        - name: ARE_API_KEY
          valueFrom:
            secretKeyRef:
              name: are-secrets
              key: api-key
```

## 📚 Examples

See the `examples/` directory for complete working examples:

- **Basic Goal Processing**: `examples/basic_goal.py`
- **Real-time Event Handling**: `examples/event_streaming.py`
- **Agent-specific Operations**: `examples/agent_operations.py`
- **Error Handling**: `examples/error_handling.py`
- **Batch Processing**: `examples/batch_operations.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This SDK is part of the Rekindle platform and is licensed under the same terms as the main platform.

## 🆘 Support

- **Documentation**: Full API docs available at `/docs`
- **Issues**: Report bugs on GitHub
- **Discussions**: Join the developer community
- **Enterprise Support**: Contact sales@rekindle.ai

---

**ARE SDK enables any part of Rekindle to harness the power of autonomous AI agents, creating a truly intelligent revenue platform.**