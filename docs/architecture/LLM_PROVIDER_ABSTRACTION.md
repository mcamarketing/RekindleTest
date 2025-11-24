# LLM Provider Abstraction Layer

**Date**: 2025-01-23
**Status**: ✅ Complete
**Purpose**: Model-agnostic architecture supporting GPT-4, Llama, Mixtral, and hybrid routing

---

## Overview

The LLM Provider Abstraction Layer decouples RekindlePro from any single LLM vendor, enabling:

✅ **Cost Optimization**: Switch to cheaper models (10x cost savings)
✅ **Full Ownership**: Run open-source models locally (data privacy, compliance)
✅ **Hybrid Routing**: GPT-4 for complex, Llama for simple (best of both worlds)
✅ **Easy Migration**: Swap models without changing application code
✅ **A/B Testing**: Compare model performance in production

---

## Architecture

```
Application Code
     ↓
ModelRouter (intelligent routing)
     ↓
├── OpenAIProvider (GPT-4, GPT-4o, GPT-4o-mini)
├── LlamaProvider (Llama-3, Llama-3.1) → Replicate, Together AI, vLLM, Ollama
├── MixtralProvider (Mixtral-8x7B, Mixtral-8x22B) → Together AI, vLLM, Ollama
└── [Future: AnthropicProvider, GeminiProvider, Custom Models]
```

**Key Benefit**: Change one line of config to switch from GPT-4 ($30/1M tokens) to Llama-3 ($0.90/1M tokens) = **33x cost reduction**.

---

## Components

### 1. Base Provider (`base_provider.py`)

**Purpose**: Abstract interface that all providers implement.

**Key Classes**:

```python
class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat_completion(messages, model, temperature, max_tokens) -> LLMResponse

    @abstractmethod
    async def fine_tune(training_file_path, base_model) -> Dict

    @abstractmethod
    async def get_fine_tuning_status(job_id) -> Dict

    @abstractmethod
    def get_model_info(model) -> ModelInfo

    @abstractmethod
    def list_models() -> List[ModelInfo]
```

**LLMResponse** (standardized across all providers):
```python
@dataclass
class LLMResponse:
    content: str  # Generated text
    model: str  # Model used
    provider: str  # Provider name (openai, llama, mixtral)
    tokens_used: int  # Total tokens
    cost: float  # Cost in USD
    latency_ms: int  # Response time
    metadata: Dict  # Additional info
```

**ModelInfo**:
```python
@dataclass
class ModelInfo:
    name: str
    provider: str
    capabilities: List[ModelCapability]  # CHAT, FINE_TUNING, EMBEDDINGS
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    context_window: int
    supports_fine_tuning: bool
    supports_local_deployment: bool
```

---

### 2. OpenAI Provider (`openai_provider.py`)

**Purpose**: Wrapper for OpenAI GPT-4 models.

**Models Supported**:
- `gpt-4o`: $2.50 input / $10 output per 1M tokens (128K context)
- `gpt-4o-mini`: $0.15 input / $0.60 output per 1M tokens (128K context) **[Best for production]**
- `gpt-4`: $30 input / $60 output per 1M tokens (8K context)

**Usage**:
```python
from backend.rex.llm_providers import OpenAIProvider

provider = OpenAIProvider({"api_key": os.getenv("OPENAI_API_KEY")})

response = await provider.chat_completion(
    messages=[
        {"role": "system", "content": "You are a sales expert"},
        {"role": "user", "content": "Write a cold email"}
    ],
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=500
)

print(response.content)  # Generated email
print(f"Cost: ${response.cost:.4f}")  # $0.0003
print(f"Latency: {response.latency_ms}ms")  # 850ms
```

**Fine-Tuning**:
```python
result = await provider.fine_tune(
    training_file_path="./training.jsonl",
    base_model="gpt-4o-mini",
    suffix="rekindle-v2-1-0"
)

# Returns: {"job_id": "ftjob-abc", "status": "queued"}
```

---

### 3. Llama Provider (`llama_provider.py`)

**Purpose**: Support for Meta's Llama-3 models via multiple backends.

**Models Supported**:
- `llama-3.1-70b`: $0.90 per 1M tokens (128K context) **[Approaching GPT-4 quality]**
- `llama-3.1-8b`: $0.20 per 1M tokens (128K context) **[Fast & cheap]**
- `llama-3-70b`: $0.90 per 1M tokens (8K context)

**Backends Supported**:

1. **Replicate** (Hosted, pay-per-use)
```python
provider = LlamaProvider({
    "backend": "replicate",
    "api_key": os.getenv("REPLICATE_API_KEY")
})
```

2. **Together AI** (Hosted, cheap, fast)
```python
provider = LlamaProvider({
    "backend": "together",
    "api_key": os.getenv("TOGETHER_API_KEY")
})
```

3. **vLLM** (Self-hosted, OpenAI-compatible)
```python
provider = LlamaProvider({
    "backend": "vllm",
    "base_url": "http://localhost:8000/v1"
})
# Cost: $0 (local deployment)
```

4. **Ollama** (Self-hosted, Docker-based)
```python
provider = LlamaProvider({
    "backend": "ollama"
})
# Cost: $0 (local deployment)
```

**Usage**:
```python
response = await provider.chat_completion(
    messages=[...],
    model="llama-3.1-8b",
    temperature=0.7,
    max_tokens=500
)

print(f"Cost: ${response.cost:.4f}")  # $0.00007 (14x cheaper than GPT-4o-mini)
```

**Local Deployment** (vLLM):
```bash
# Install vLLM
pip install vllm

# Start server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --port 8000

# Use from Python
provider = LlamaProvider({"backend": "vllm"})
response = await provider.chat_completion(...)  # $0 cost
```

---

### 4. Mixtral Provider (`mixtral_provider.py`)

**Purpose**: Support for Mistral AI's Mixtral models (mixture-of-experts).

**Models Supported**:
- `mixtral-8x7b`: $0.60 per 1M tokens (32K context) **[Best bang for buck]**
- `mixtral-8x22b`: $1.20 per 1M tokens (65K context) **[Approaching GPT-4, 1/5th cost]**

**Key Advantages**:
- Mixtral-8x7B matches GPT-3.5 performance at 1/10th cost
- Mixtral-8x22B approaches GPT-4 performance at 1/5th cost
- Fully open-source (Apache 2.0 license)
- Can be self-hosted

**Usage** (same as LlamaProvider):
```python
from backend.rex.llm_providers import MixtralProvider

provider = MixtralProvider({
    "backend": "together",
    "api_key": os.getenv("TOGETHER_API_KEY")
})

response = await provider.chat_completion(
    messages=[...],
    model="mixtral-8x7b",
    temperature=0.7,
    max_tokens=500
)

print(f"Cost: ${response.cost:.4f}")  # $0.00006 (15x cheaper than GPT-4o-mini)
```

---

### 5. Model Router (`model_router.py`)

**Purpose**: Intelligent routing between providers based on cost, latency, task complexity.

**Routing Strategies**:

1. **CHEAPEST**: Always use cheapest model
2. **FASTEST**: Always use fastest (local) model
3. **BEST_QUALITY**: Always use highest quality (GPT-4)
4. **SMART**: Intelligent routing based on task complexity **[Recommended]**
5. **AB_TEST**: Random routing for performance comparison

**Usage**:
```python
from backend.rex.llm_providers import (
    OpenAIProvider,
    LlamaProvider,
    MixtralProvider,
    ModelRouter,
    RoutingStrategy
)

# Initialize providers
providers = {
    "openai": OpenAIProvider({"api_key": os.getenv("OPENAI_API_KEY")}),
    "llama": LlamaProvider({"backend": "together", "api_key": ...}),
    "mixtral": MixtralProvider({"backend": "together", "api_key": ...}),
}

# Create router
router = ModelRouter(providers, default_strategy=RoutingStrategy.SMART)

# Smart routing (automatic provider selection)
response = await router.route(
    messages=[
        {"role": "user", "content": "Write a short cold email"}
    ],
    task_type="simple"  # Hint: simple task
)
# Routes to: mixtral/mixtral-8x7b (cheap, fast, good enough)

# Complex task
response = await router.route(
    messages=[
        {"role": "user", "content": "Analyze this 2000-word sales transcript and..."}
    ],
    task_type="complex"  # Hint: complex task
)
# Routes to: openai/gpt-4o (best quality for hard tasks)

# Explicit selection (bypass routing)
response = await router.route(
    messages=[...],
    provider="llama",
    model="llama-3.1-70b"
)
```

**Smart Routing Heuristics**:
- Short messages (<200 chars) → Mixtral-8x7B (cheap)
- Long messages (>1000 chars) → GPT-4o (complex understanding)
- Multi-turn conversations → GPT-4o (context retention)
- Sentiment analysis → Llama-3.1-8B (fast, specialized)
- Simple classification → Mixtral-8x7B (good enough)

**Performance Tracking**:
```python
report = router.get_performance_report()

# Returns:
{
    "openai/gpt-4o": {
        "avg_latency_ms": 1200,
        "avg_cost": 0.0045,
        "success_rate": 0.99,
        "total_requests": 1500
    },
    "mixtral/mixtral-8x7b": {
        "avg_latency_ms": 650,
        "avg_cost": 0.0003,
        "success_rate": 0.97,
        "total_requests": 8500
    }
}
```

---

## Cost Comparison

### Example: 100,000 messages/month

**Assumptions**:
- Average message: 500 input tokens, 200 output tokens (700 total)
- 100K messages/month = 70M tokens/month

| Provider | Model | Cost/Month | Savings vs GPT-4 |
|----------|-------|------------|------------------|
| **OpenAI** | GPT-4 | $3,150 | Baseline |
| **OpenAI** | GPT-4o | $490 | 84% |
| **OpenAI** | GPT-4o-mini | $42 | 99% |
| **Llama** | Llama-3.1-70B | $63 | 98% |
| **Llama** | Llama-3.1-8B | $14 | 99.6% |
| **Mixtral** | Mixtral-8x7B | $42 | 99% |
| **Mixtral** | Mixtral-8x22B | $84 | 97% |
| **Local vLLM** | Llama-3.1-8B | $0* | 100% |

*Assumes self-hosted on existing infrastructure

**Hybrid Approach** (Recommended):
- 20% complex tasks → GPT-4o: $98/month
- 80% simple tasks → Mixtral-8x7B: $27/month
- **Total: $125/month (96% savings vs GPT-4)**

---

## Migration Strategy

### Phase 1: Add Abstraction Layer (Week 1)
**Goal**: No breaking changes, GPT-4 remains default

1. Install dependencies:
```bash
pip install replicate together ollama openai
```

2. Update existing code to use abstraction:
```python
# Before:
from openai import AsyncOpenAI
client = AsyncOpenAI()
response = await client.chat.completions.create(...)

# After:
from backend.rex.llm_providers import OpenAIProvider
provider = OpenAIProvider({"api_key": ...})
response = await provider.chat_completion(...)
```

**Status**: No risk, same behavior, foundation in place

---

### Phase 2: Add Mixtral for Simple Tasks (Week 2)
**Goal**: Route 50% of simple tasks to Mixtral, save 50% cost

1. Initialize Mixtral provider:
```python
mixtral = MixtralProvider({
    "backend": "together",
    "api_key": os.getenv("TOGETHER_API_KEY")
})
```

2. Set up router:
```python
router = ModelRouter(
    providers={"openai": openai_provider, "mixtral": mixtral},
    default_strategy=RoutingStrategy.SMART
)
```

3. Update sentiment analyzer to use router:
```python
# In sentiment_analyzer.py
response = await router.route(
    messages=[...],
    task_type="sentiment"  # Routes to Mixtral (cheaper)
)
```

**Expected Impact**:
- 50% of sentiment analysis → Mixtral
- Cost reduction: ~50% on sentiment (small volume)
- Quality: Same or better (Mixtral excels at classification)

---

### Phase 3: Add Llama for High-Volume Tasks (Week 3-4)
**Goal**: Route 80% of personalization tasks to Llama-3.1-70B

1. Initialize Llama provider:
```python
llama = LlamaProvider({
    "backend": "together",
    "api_key": os.getenv("TOGETHER_API_KEY")
})
```

2. Update router:
```python
router = ModelRouter(
    providers={"openai": openai_provider, "llama": llama, "mixtral": mixtral},
    default_strategy=RoutingStrategy.SMART
)
```

3. Route message generation:
```python
# In PersonalizerAgent
response = await router.route(
    messages=[...],
    task_type="simple" if len(message) < 500 else "complex"
)
```

**Expected Impact**:
- 80% of messages → Llama-3.1-70B
- 20% complex → GPT-4o
- Cost reduction: ~85% on message generation
- **Total cost savings: $400/month → $60/month (85% savings)**

---

### Phase 4: Self-Host Llama with vLLM (Month 2)
**Goal**: Zero inference cost for high-volume production

1. Set up vLLM server (GPU required):
```bash
# AWS: g4dn.xlarge ($0.526/hour = $380/month)
# Or Render GPU: $100-200/month

pip install vllm
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --port 8000 \
    --gpu-memory-utilization 0.9
```

2. Update provider:
```python
llama_local = LlamaProvider({
    "backend": "vllm",
    "base_url": "http://your-server:8000/v1"
})
```

3. Route high-volume tasks to local:
```python
router = ModelRouter(
    providers={
        "openai": openai_provider,  # Complex only
        "llama_local": llama_local,  # High-volume
        "llama_cloud": llama_cloud,  # Overflow
    },
    default_strategy=RoutingStrategy.SMART
)
```

**Expected Impact**:
- Inference cost: $0/month (after GPU server cost)
- GPU server: $380/month (AWS) or $150/month (Render GPU)
- Break-even at: ~20K messages/month
- **At 100K messages/month: $530/month savings vs cloud Llama**

---

### Phase 5: Fine-Tune Llama on Proprietary Data (Month 3)
**Goal**: Proprietary model that outperforms GPT-4

1. Export training data (use existing Stage 3 pipeline)
2. Fine-tune Llama-3.1-70B on Together AI or locally
3. Deploy fine-tuned model
4. Compare performance vs GPT-4

**Expected Impact**:
- Fine-tuned Llama matches or exceeds GPT-4 on your specific use case
- Cost: 33x cheaper than GPT-4
- Full ownership: No vendor lock-in
- **Defensive moat: Competitors can't access your model**

---

## Integration with Existing Code

### Update Sentiment Analyzer

**Before**:
```python
# sentiment_analyzer.py
from openai import AsyncOpenAI

class SentimentAnalyzer:
    def __init__(self, openai_api_key):
        self.client = AsyncOpenAI(api_key=openai_api_key)

    async def analyze(self, text):
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[...]
        )
```

**After**:
```python
# sentiment_analyzer.py
from backend.rex.llm_providers import ModelRouter, RoutingStrategy

class SentimentAnalyzer:
    def __init__(self, router: ModelRouter):
        self.router = router

    async def analyze(self, text):
        response = await self.router.route(
            messages=[...],
            task_type="sentiment",  # Routes to Mixtral (cheap, fast)
            strategy=RoutingStrategy.CHEAPEST
        )
```

---

### Update Training Pipeline

**Before**:
```python
# model_trainer.py
from openai import AsyncOpenAI

class GPT4ModelTrainer:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.base_model = "gpt-4o-2024-08-06"
```

**After**:
```python
# model_trainer.py (now model-agnostic)
from backend.rex.llm_providers import BaseLLMProvider

class UniversalModelTrainer:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def fine_tune(self, training_file_path, base_model):
        # Works with OpenAI, Llama, Mixtral, etc.
        result = await self.provider.fine_tune(
            training_file_path=training_file_path,
            base_model=base_model
        )
```

---

## Benchmarking & A/B Testing

### Compare Models on Your Data

```python
from backend.rex.llm_providers import ModelRouter, RoutingStrategy

router = ModelRouter(providers={...})

# Test messages
test_messages = [
    {"role": "user", "content": "Write a cold email to a VP of Sales in SaaS"}
]

# Benchmark all models
models_to_test = [
    ("openai", "gpt-4o"),
    ("openai", "gpt-4o-mini"),
    ("llama", "llama-3.1-70b"),
    ("mixtral", "mixtral-8x7b"),
]

results = []
for provider, model in models_to_test:
    response = await router.route(
        messages=test_messages,
        provider=provider,
        model=model
    )

    results.append({
        "provider": provider,
        "model": model,
        "content": response.content,
        "cost": response.cost,
        "latency_ms": response.latency_ms,
        "tokens": response.tokens_used,
    })

# Compare
for r in sorted(results, key=lambda x: x["cost"]):
    print(f"{r['provider']}/{r['model']}: ${r['cost']:.4f}, {r['latency_ms']}ms")
```

### A/B Test in Production

```python
# Set up A/B test: 90% Mixtral, 10% GPT-4o
router = ModelRouter(
    providers={...},
    default_strategy=RoutingStrategy.AB_TEST
)

# Track outcomes
for outcome in outcomes:
    model_used = outcome.metadata["model"]
    reply_rate = outcome.replied / outcome.sent

    # Compare: Does Mixtral match GPT-4o quality?
```

---

## Recommendations

### For Early Stage (0-1,000 users)
**Use**: GPT-4o-mini via OpenAI
- **Why**: Fast to set up, good quality, low volume = low cost
- **Cost**: ~$50/month for 10K messages
- **Migration path**: Already using abstraction layer, easy to switch later

### For Growth Stage (1,000-10,000 users)
**Use**: Hybrid routing (Mixtral + GPT-4o)
- **Why**: 85% cost savings, maintain quality on complex tasks
- **Cost**: ~$150/month for 100K messages
- **Setup**: Add Together AI account, configure router

### For Scale Stage (10,000+ users)
**Use**: Self-hosted Llama-3.1-70B + GPT-4o fallback
- **Why**: Zero inference cost, full control, proprietary fine-tuned model
- **Cost**: $380/month GPU + $50/month GPT-4o fallback = $430/month for 500K messages
- **Break-even**: 20K messages/month

### For Enterprise/Exit (100,000+ users)
**Use**: Fine-tuned Llama-3.1-70B (self-hosted)
- **Why**: Defensive moat, best performance on your data, zero vendor risk
- **Cost**: $500-1,000/month infrastructure
- **Value**: Proprietary model = acquisition premium

---

## Files Created

```
backend/rex/llm_providers/
  __init__.py                    # Package exports
  base_provider.py               # Abstract base class
  openai_provider.py             # GPT-4, GPT-4o, GPT-4o-mini
  llama_provider.py              # Llama-3, Llama-3.1 (multiple backends)
  mixtral_provider.py            # Mixtral-8x7B, Mixtral-8x22B
  model_router.py                # Intelligent routing system

docs/architecture/
  LLM_PROVIDER_ABSTRACTION.md    # This file
```

---

## Next Steps

1. **Week 1**: Integrate abstraction layer (no behavior change)
2. **Week 2**: Add Mixtral for sentiment analysis (50% cost savings)
3. **Week 3**: Route 80% to Llama (85% total savings)
4. **Month 2**: Self-host Llama with vLLM (zero inference cost)
5. **Month 3**: Fine-tune proprietary model (defensive moat)

---

**Status**: ✅ **Architecture Complete** | 🚀 **Ready for Integration**

**Next Action**: Update sentiment_analyzer.py to use ModelRouter
