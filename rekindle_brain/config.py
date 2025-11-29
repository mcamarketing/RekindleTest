"""
Rekindle Brain Configuration

Defines model specifications, training parameters, and infrastructure settings.
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class ModelType(Enum):
    """Available base model types"""
    MISTRAL_7B = "mistral-7b"
    ZEPHYR_7B = "zephyr-7b"
    DEEPSEEK_CODER = "deepseek-coder"

class QuantizationType(Enum):
    """Quantization formats"""
    GGUF = "gguf"
    EXLLAMA = "exllama"
    AWQ = "awq"
    GPTQ = "gptq"

class DeploymentType(Enum):
    """Deployment environments"""
    CPU = "cpu"
    GPU = "gpu"

@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    source: str
    license: str
    rationale: str
    huggingface_repo: Optional[str] = None
    quantization_formats: List[QuantizationType] = field(default_factory=list)
    context_window: int = 4096
    parameters: int = 7_000_000_000  # 7B parameters

@dataclass
class TrainingPhase:
    """Configuration for a training phase"""
    name: str
    description: str
    steps: List[str]
    estimated_duration_weeks: int
    compute_requirements: str
    data_requirements: List[str]

@dataclass
class InfrastructureConfig:
    """Infrastructure configuration"""
    deployment_type: DeploymentType
    hardware_requirements: Dict[str, Any]
    storage_requirements: Dict[str, Any]
    cost_estimates: Dict[str, float]

@dataclass
class BrainConfig:
    """Main Rekindle Brain configuration"""

    # Model configurations
    models: Dict[ModelType, ModelConfig] = field(default_factory=lambda: {
        ModelType.MISTRAL_7B: ModelConfig(
            name="Mistral-7B",
            source="mistral.ai",
            license="Apache 2.0",
            rationale="Best performance/size ratio, easy to quantize and fine-tune",
            huggingface_repo="mistralai/Mistral-7B-v0.1",
            quantization_formats=[QuantizationType.GGUF, QuantizationType.EXLLAMA],
            context_window=8192
        ),
        ModelType.ZEPHYR_7B: ModelConfig(
            name="Zephyr-7B",
            source="HuggingFace",
            license="MIT",
            rationale="Strong instruction-following out of the box",
            huggingface_repo="HuggingFaceH4/zephyr-7b-beta",
            quantization_formats=[QuantizationType.GGUF, QuantizationType.AWQ],
            context_window=4096
        ),
        ModelType.DEEPSEEK_CODER: ModelConfig(
            name="DeepSeek-Coder",
            source="deepseek.com",
            license="MIT",
            rationale="Useful for agent-based code/task workflows",
            huggingface_repo="deepseek-ai/deepseek-coder-6.7b-base",
            quantization_formats=[QuantizationType.GGUF, QuantizationType.GPTQ],
            context_window=16384,
            parameters=6_700_000_000
        )
    })

    # Training phases
    training_phases: List[TrainingPhase] = field(default_factory=lambda: [
        TrainingPhase(
            name="Phase 1 - Foundation Prep",
            description="Prepare models and infrastructure for training",
            steps=[
                "Quantize model to 4-bit for CPU feasibility (GGUF/ExLlama)",
                "Prepare RAG layer with vector DB (e.g., Weaviate or Qdrant)",
                "Tokenize sample proprietary outcome data (calls, CRM, sequences)"
            ],
            estimated_duration_weeks=4,
            compute_requirements="CPU with 16GB RAM",
            data_requirements=["Sample business data", "Vector database setup"]
        ),
        TrainingPhase(
            name="Phase 2 - Domain Tuning + RAG",
            description="Fine-tune on business domain and integrate social intelligence",
            steps=[
                "LoRA fine-tune using sales/revenue outcome data, rejection handling, persona labeling",
                "Use OpenHermes/SalesGPT datasets as scaffolding if needed",
                "Layer Reddit + X behavioral examples via RAG for real-time tone/mood insights"
            ],
            estimated_duration_weeks=6,
            compute_requirements="GPU (A100 recommended)",
            data_requirements=["Proprietary business data", "Social media datasets", "Sales conversation transcripts"]
        ),
        TrainingPhase(
            name="Phase 3 - Continual Learning & Feedback Loop",
            description="Implement ongoing learning from business outcomes",
            steps=[
                "Ingest fresh data weekly from customer replies, win/loss outcomes, objections, and meeting results",
                "Use Critic agent to evaluate success and identify new training signals",
                "Auto-update embedding store + fine-tune monthly on top outcomes"
            ],
            estimated_duration_weeks=12,  # Ongoing
            compute_requirements="GPU for fine-tuning, CPU for inference",
            data_requirements=["Continuous data pipeline", "Critic evaluation data", "Performance metrics"]
        )
    ])

    # Infrastructure configurations
    infrastructure: Dict[DeploymentType, InfrastructureConfig] = field(default_factory=lambda: {
        DeploymentType.CPU: InfrastructureConfig(
            deployment_type=DeploymentType.CPU,
            hardware_requirements={
                "cpu": "8+ cores",
                "ram": "16GB+",
                "storage": "500GB SSD"
            },
            storage_requirements={
                "vector_db": "Weaviate/Qdrant",
                "model_storage": "Local SSD",
                "data_cache": "100GB"
            },
            cost_estimates={
                "monthly_compute": 20.0,
                "storage": 15.0,
                "total": 35.0
            }
        ),
        DeploymentType.GPU: InfrastructureConfig(
            deployment_type=DeploymentType.GPU,
            hardware_requirements={
                "gpu": "A100 or equivalent",
                "cpu": "16+ cores",
                "ram": "64GB+",
                "storage": "1TB NVMe"
            },
            storage_requirements={
                "vector_db": "Weaviate/Qdrant (cloud)",
                "model_storage": "Cloud storage",
                "data_cache": "500GB"
            },
            cost_estimates={
                "monthly_compute": 75.0,
                "storage": 25.0,
                "data_transfer": 15.0,
                "total": 115.0
            }
        )
    })

    # Training parameters
    training_config: Dict[str, Any] = field(default_factory=lambda: {
        "lora_config": {
            "r": 16,
            "lora_alpha": 32,
            "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
            "lora_dropout": 0.05,
            "bias": "none",
            "task_type": "CAUSAL_LM"
        },
        "training_args": {
            "per_device_train_batch_size": 4,
            "gradient_accumulation_steps": 4,
            "warmup_steps": 100,
            "max_steps": 1000,
            "learning_rate": 2e-4,
            "fp16": True,
            "logging_steps": 10,
            "save_strategy": "steps",
            "save_steps": 500,
            "evaluation_strategy": "steps",
            "eval_steps": 500,
            "load_best_model_at_end": True
        },
        "quantization_config": {
            "load_in_4bit": True,
            "bnb_4bit_compute_dtype": "float16",
            "bnb_4bit_use_double_quant": True,
            "bnb_4bit_quant_type": "nf4"
        }
    })

    # Data pipeline configuration
    data_config: Dict[str, Any] = field(default_factory=lambda: {
        "vector_db": {
            "type": "weaviate",  # or "qdrant"
            "collection_name": "rekindle_brain_embeddings",
            "vector_size": 4096,
            "distance_metric": "cosine"
        },
        "embedding_model": {
            "name": "text-embedding-ada-002",
            "provider": "openai",
            "dimensions": 1536
        },
        "data_sources": {
            "proprietary": ["crm_data", "call_transcripts", "outcome_data"],
            "social": ["reddit", "twitter", "hackernews"],
            "public": ["openhermes", "salesgpt", "business_literature"]
        }
    })

    # Security and compliance
    security_config: Dict[str, Any] = field(default_factory=lambda: {
        "privacy_filters": [
            r'\b\d{3,}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP addresses
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b',  # Credit cards
            r'\b\w{2,}\s+\w{2,}\s+\d{1,5}\b',  # Addresses
        ],
        "content_filters": [
            "hate_speech",
            "personal_attacks",
            "illegal_activities",
            "sensitive_personal_data"
        ],
        "audit_logging": {
            "enabled": True,
            "log_level": "INFO",
            "retention_days": 90
        }
    })

    # Performance targets
    performance_targets: Dict[str, Any] = field(default_factory=lambda: {
        "response_time_seconds": 5.0,
        "context_window_tokens": 8192,
        "accuracy_threshold": 0.85,
        "cost_per_query_usd": 0.01,
        "uptime_percentage": 99.9
    })

    # Agent integration settings
    agent_integration: Dict[str, Any] = field(default_factory=lambda: {
        "are_endpoints": {
            "planner": "http://localhost:8000/api/are/planner",
            "critic": "http://localhost:8000/api/are/critic",
            "social_listener": "http://localhost:8000/api/are/social",
            "guardrail": "http://localhost:8000/api/are/guardrail"
        },
        "communication_protocol": {
            "request_format": "json",
            "response_format": "json",
            "timeout_seconds": 30,
            "retry_attempts": 3
        },
        "data_sharing": {
            "training_signals": True,
            "social_intelligence": True,
            "performance_metrics": True,
            "anonymized_only": True
        }
    })

    def get_model_config(self, model_type: ModelType) -> ModelConfig:
        """Get configuration for a specific model"""
        return self.models[model_type]

    def get_training_phase(self, phase_index: int) -> TrainingPhase:
        """Get training phase by index"""
        return self.training_phases[phase_index]

    def get_infrastructure_config(self, deployment_type: DeploymentType) -> InfrastructureConfig:
        """Get infrastructure configuration"""
        return self.infrastructure[deployment_type]

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "models": {k.value: v.__dict__ for k, v in self.models.items()},
            "training_phases": [phase.__dict__ for phase in self.training_phases],
            "infrastructure": {k.value: v.__dict__ for k, v in self.infrastructure.items()},
            "training_config": self.training_config,
            "data_config": self.data_config,
            "security_config": self.security_config,
            "performance_targets": self.performance_targets,
            "agent_integration": self.agent_integration
        }

# Global configuration instance
brain_config = BrainConfig()