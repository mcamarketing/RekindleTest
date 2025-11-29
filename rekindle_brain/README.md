# 🧠 Rekindle Brain - Autonomous Business Intelligence LLM

## Overview

The Rekindle Brain is a specialized large language model designed to master behavioral science, marketing, sales, negotiation, and dynamic business strategy. It evolves from an efficient open-source base (Mistral-7B) into a highly specialized business oracle using real business outcomes and scraped social intelligence.

## Architecture

### Core Components
- **Base Models**: Mistral-7B, Zephyr-7B, DeepSeek-Coder
- **Training Strategy**: 3-phase approach (Foundation → Domain Tuning → Continual Learning)
- **RAG Layer**: Vector database for real-time social intelligence
- **Agent Integration**: ARE system integration (Planner, Critic, Social Listener, Guardrail)
- **Infrastructure**: CPU pre-launch, GPU post-launch scaling

### Training Phases

#### Phase 1: Foundation Prep
- Quantize models to 4-bit GGUF/ExLlama for CPU feasibility
- Prepare RAG layer with Weaviate/Qdrant vector database
- Tokenize sample proprietary outcome data (calls, CRM, sequences)

#### Phase 2: Domain Tuning + RAG
- LoRA fine-tune using sales/revenue outcome data
- Integrate rejection handling and persona labeling
- Layer Reddit/X behavioral examples via RAG for real-time insights

#### Phase 3: Continual Learning & Feedback Loop
- Weekly ingestion of fresh customer data (replies, outcomes, objections)
- Critic agent evaluation for training signals
- Monthly auto-updates to embedding store and fine-tuning

## Quick Start

### Installation
```bash
cd rekindle_brain
pip install -r requirements.txt
```

### Basic Usage
```python
from rekindle_brain import RekindleBrain

brain = RekindleBrain()
response = brain.generate_business_strategy(
    goal="Increase ARR by 30%",
    context="SaaS company with 50 employees",
    constraints="Budget: $50K/month"
)
```

### Training
```python
from rekindle_brain.training import BrainTrainer

trainer = BrainTrainer(model_name="mistral-7b")
trainer.fine_tune_on_business_data(
    data_path="data/business_outcomes.jsonl",
    output_dir="models/fine_tuned"
)
```

## Model Specifications

### Base Models
| Model | Source | License | Rationale |
|-------|--------|---------|-----------|
| Mistral-7B | mistral.ai | Apache 2.0 | Best performance/size ratio, easy quantization |
| Zephyr-7B | HuggingFace | MIT | Strong instruction-following |
| DeepSeek-Coder | deepseek.com | MIT | Agent-based code/task workflows |

### Quantization
- **GGUF Format**: 4-bit quantization for CPU deployment
- **ExLlama**: Efficient inference on consumer hardware
- **Target**: Sub-5s response times

## Data Sources

### Proprietary Data
- Customer call transcripts and outcomes
- CRM data and conversion sequences
- Win/loss analysis and objection handling
- Meeting booking success rates

### Social Intelligence
- Reddit business/marketing communities
- Twitter/X industry conversations
- HackerNews startup discussions
- Behavioral science research papers

### Public Datasets
- OpenHermes conversational data
- SalesGPT training examples
- Business negotiation transcripts
- Marketing copy datasets

## Agent Integration

### ARE System Integration
- **Planner**: Routes goal decomposition to Brain or CrewAI agents
- **Critic**: Labels successful/failed patterns for training signals
- **Social Listener**: Ingests social data and converts to embeddings
- **Guardrail**: Validates prompt security and compliance

### Communication Protocol
```python
# Brain request from ARE Planner
request = {
    "task_type": "business_strategy",
    "goal": "Optimize pricing model",
    "context": "SaaS company, 200 customers",
    "constraints": {"budget": 50000, "timeline": "3 months"},
    "social_intel": ["competitor_pricing_trends", "customer_pain_points"]
}

# Brain response
response = {
    "strategy": "Dynamic pricing with A/B testing",
    "rationale": "Based on competitor analysis and customer feedback",
    "action_plan": ["Implement pricing tiers", "Run A/B tests"],
    "confidence_score": 0.87,
    "training_signals": ["pricing_optimization_success"]
}
```

## Infrastructure

### Pre-Launch (CPU)
- **Hardware**: Consumer CPU with 16GB+ RAM
- **Storage**: Local SSD + Weaviate vector DB
- **Serving**: llama.cpp or ExLlama2
- **Cost**: ~$20/month (storage)

### Post-Launch (GPU)
- **Hardware**: A100 GPU via RunPod/LambdaLabs
- **Serving**: vLLM + FlashAttention2
- **Scaling**: Auto-scaling based on load
- **Cost**: $50-100/month

## Security & Compliance

### Data Privacy
- **Anonymization**: Automatic PII redaction
- **Consent Filters**: Opt-out support for social data
- **Source Tracing**: Complete data provenance
- **Compliance**: GDPR, CCPA, SOC2 alignment

### Model Safety
- **Bias Mitigation**: Regular bias audits
- **Content Filtering**: Business-appropriate responses
- **Jailbreak Prevention**: Prompt engineering safeguards
- **Audit Logging**: Complete interaction history

## Performance Benchmarks

### Target Metrics
- **Response Time**: <5 seconds
- **Context Window**: 8K-32K tokens
- **Accuracy**: 85%+ on business strategy tasks
- **Cost Efficiency**: <$0.01 per query

### Training Metrics
- **Fine-tuning Cost**: $250-500 per run
- **Convergence**: 3-5 epochs for domain adaptation
- **Data Efficiency**: 10K+ high-quality examples

## Development Roadmap

### Phase 1 (Foundation) - 4 weeks
- [ ] Model quantization and CPU deployment
- [ ] RAG layer with vector database
- [ ] Basic training data pipeline
- [ ] ARE agent integration stubs

### Phase 2 (Domain Tuning) - 6 weeks
- [ ] LoRA fine-tuning on business data
- [ ] Social intelligence ingestion
- [ ] Performance benchmarking
- [ ] Security and compliance implementation

### Phase 3 (Continual Learning) - Ongoing
- [ ] Weekly data ingestion pipeline
- [ ] Critic evaluation integration
- [ ] Monthly model updates
- [ ] Performance monitoring and optimization

## API Reference

### Core Methods

#### `generate_business_strategy(goal, context, constraints)`
Generates comprehensive business strategies with actionable plans.

#### `analyze_market_opportunity(data, competitors, trends)`
Analyzes market opportunities using social intelligence and business data.

#### `optimize_sales_sequence(current_sequence, outcomes, objections)`
Optimizes sales sequences based on performance data and objections.

#### `negotiate_terms(proposal, constraints, objectives)`
Provides negotiation strategies and counter-proposals.

### Training Methods

#### `fine_tune_on_business_data(data_path, config)`
Fine-tunes model on proprietary business data.

#### `update_social_intelligence(social_data, embeddings)`
Updates RAG layer with fresh social intelligence.

#### `evaluate_and_update(success_patterns, failure_patterns)`
Uses critic feedback to update model weights.

## Contributing

### Development Setup
1. Clone repository
2. Install dependencies: `pip install -r requirements-dev.txt`
3. Set up pre-commit hooks: `pre-commit install`
4. Run tests: `pytest`

### Code Standards
- **Type Hints**: Full Python typing
- **Documentation**: Google-style docstrings
- **Testing**: 90%+ coverage required
- **Security**: Regular dependency updates

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## Support

- **Documentation**: This README and docstrings
- **Issues**: GitHub issues for bugs and features
- **Discussions**: GitHub discussions for questions
- **Security**: security@rekindle.ai for security issues

---

**Status**: 🧠 **Development Ready** | **Architecture**: Specialized Business LLM
**Models**: Mistral-7B + Zephyr-7B + DeepSeek-Coder | **Training**: 3-Phase Continual Learning
**Integration**: ARE Agent System | **Infrastructure**: CPU→GPU Scaling
**Security**: Enterprise-grade privacy and compliance