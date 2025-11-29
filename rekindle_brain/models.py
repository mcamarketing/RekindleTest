"""
Model Manager for Rekindle Brain

Handles loading, managing, and switching between different LLM models
(Mistral-7B, Zephyr-7B, DeepSeek-Coder) with quantization support.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import torch

from .config import BrainConfig, ModelType, DeploymentType, QuantizationType, ModelConfig

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages LLM models for the Rekindle Brain"""

    def __init__(self, config: BrainConfig):
        self.config = config
        self.loaded_models: Dict[ModelType, Any] = {}
        self.model_configs: Dict[ModelType, ModelConfig] = config.models
        self.deployment_type: Optional[DeploymentType] = None
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)

    async def initialize(self, deployment_type: DeploymentType):
        """Initialize model manager for specific deployment type"""
        self.deployment_type = deployment_type
        logger.info(f"Initializing ModelManager for {deployment_type.value} deployment")

        # Set up environment based on deployment type
        if deployment_type == DeploymentType.CPU:
            os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Disable GPU
            torch.set_num_threads(8)  # Use 8 CPU threads
        elif deployment_type == DeploymentType.GPU:
            if not torch.cuda.is_available():
                raise RuntimeError("GPU deployment requested but CUDA not available")
            torch.set_num_threads(torch.cuda.device_count() * 4)

    async def load_base_models(self):
        """Load all configured base models"""
        logger.info("Loading base models...")

        for model_type, model_config in self.model_configs.items():
            try:
                await self._load_model(model_type, model_config)
                logger.info(f"Loaded {model_type.value}")
            except Exception as e:
                logger.warning(f"Failed to load {model_type.value}: {e}")
                # Continue with other models

    async def _load_model(self, model_type: ModelType, config: ModelConfig):
        """Load a specific model based on deployment type"""
        if self.deployment_type == DeploymentType.CPU:
            await self._load_cpu_model(model_type, config)
        elif self.deployment_type == DeploymentType.GPU:
            await self._load_gpu_model(model_type, config)
        else:
            raise ValueError(f"Unsupported deployment type: {self.deployment_type}")

    async def _load_cpu_model(self, model_type: ModelType, config: ModelConfig):
        """Load model optimized for CPU deployment"""
        try:
            # Try GGUF format first (most efficient for CPU)
            if QuantizationType.GGUF in config.quantization_formats:
                model_path = await self._download_or_get_gguf_model(model_type, config)
                model = await self._load_gguf_model(model_path, config)
            elif QuantizationType.EXLLAMA in config.quantization_formats:
                model_path = await self._download_or_get_exllama_model(model_type, config)
                model = await self._load_exllama_model(model_path, config)
            else:
                # Fallback to transformers with quantization
                model = await self._load_transformers_model_cpu(model_type, config)

            self.loaded_models[model_type] = model
            logger.info(f"CPU model loaded: {model_type.value}")

        except Exception as e:
            logger.error(f"Failed to load CPU model {model_type.value}: {e}")
            raise

    async def _load_gpu_model(self, model_type: ModelType, config: ModelConfig):
        """Load model optimized for GPU deployment"""
        try:
            # Use transformers with GPU acceleration
            model = await self._load_transformers_model_gpu(model_type, config)
            self.loaded_models[model_type] = model
            logger.info(f"GPU model loaded: {model_type.value}")

        except Exception as e:
            logger.error(f"Failed to load GPU model {model_type.value}: {e}")
            raise

    async def _download_or_get_gguf_model(self, model_type: ModelType, config: ModelConfig) -> Path:
        """Download or get cached GGUF model"""
        model_dir = self.model_dir / f"{model_type.value}_gguf"
        model_file = model_dir / "model.gguf"

        if model_file.exists():
            logger.info(f"Using cached GGUF model: {model_file}")
            return model_file

        # Download model (placeholder - implement actual download)
        logger.info(f"Downloading GGUF model for {model_type.value}...")
        model_dir.mkdir(exist_ok=True)

        # Mock download - in real implementation, download from HuggingFace or model hub
        await self._mock_download_model(model_file)

        return model_file

    async def _download_or_get_exllama_model(self, model_type: ModelType, config: ModelConfig) -> Path:
        """Download or get cached ExLlama model"""
        model_dir = self.model_dir / f"{model_type.value}_exllama"
        return model_dir  # ExLlama uses directory structure

    async def _load_gguf_model(self, model_path: Path, config: ModelConfig):
        """Load GGUF model using llama.cpp or similar"""
        try:
            # Import llama-cpp-python (would be installed)
            from llama_cpp import Llama

            model = Llama(
                model_path=str(model_path),
                n_ctx=config.context_window,
                n_threads=8,  # CPU threads
                verbose=False
            )

            return {
                "type": "gguf",
                "model": model,
                "config": config
            }

        except ImportError:
            raise ImportError("llama-cpp-python not installed. Install with: pip install llama-cpp-python")

    async def _load_exllama_model(self, model_path: Path, config: ModelConfig):
        """Load ExLlama model"""
        try:
            # Import exllama (would be installed)
            from exllama.model import ExLlamaModel
            from exllama.tokenizer import ExLlamaTokenizer
            from exllama.generator import ExLlamaGenerator

            # This is a simplified version - actual implementation would be more complex
            return {
                "type": "exllama",
                "model_path": model_path,
                "config": config
            }

        except ImportError:
            raise ImportError("exllama not installed. Install from: https://github.com/turboderp/exllama")

    async def _load_transformers_model_cpu(self, model_type: ModelType, config: ModelConfig):
        """Load transformers model optimized for CPU"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

            quantization_config = BitsAndBytesConfig(**self.config.training_config["quantization_config"])

            model = AutoModelForCausalLM.from_pretrained(
                config.huggingface_repo,
                quantization_config=quantization_config,
                device_map="cpu",
                torch_dtype=torch.float16
            )

            tokenizer = AutoTokenizer.from_pretrained(config.huggingface_repo)

            return {
                "type": "transformers_cpu",
                "model": model,
                "tokenizer": tokenizer,
                "config": config
            }

        except ImportError:
            raise ImportError("transformers not installed. Install with: pip install transformers accelerate bitsandbytes")

    async def _load_transformers_model_gpu(self, model_type: ModelType, config: ModelConfig):
        """Load transformers model optimized for GPU"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            model = AutoModelForCausalLM.from_pretrained(
                config.huggingface_repo,
                device_map="auto",
                torch_dtype=torch.float16,
                load_in_8bit=True  # Use 8-bit for GPU efficiency
            )

            tokenizer = AutoTokenizer.from_pretrained(config.huggingface_repo)

            return {
                "type": "transformers_gpu",
                "model": model,
                "tokenizer": tokenizer,
                "config": config
            }

        except ImportError:
            raise ImportError("transformers not installed. Install with: pip install transformers accelerate")

    async def load_fine_tuned_model(self, model_path: str):
        """Load a fine-tuned model"""
        logger.info(f"Loading fine-tuned model from {model_path}")

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto" if self.deployment_type == DeploymentType.GPU else "cpu",
                torch_dtype=torch.float16
            )

            tokenizer = AutoTokenizer.from_pretrained(model_path)

            # Store as fine-tuned version
            self.loaded_models[ModelType.MISTRAL_7B] = {
                "type": "fine_tuned",
                "model": model,
                "tokenizer": tokenizer,
                "config": self.model_configs[ModelType.MISTRAL_7B],
                "model_path": model_path
            }

            logger.info("Fine-tuned model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load fine-tuned model: {e}")
            raise

    def get_model(self, model_type: ModelType = ModelType.MISTRAL_7B):
        """Get a loaded model"""
        if model_type not in self.loaded_models:
            raise ValueError(f"Model {model_type.value} not loaded")

        return self.loaded_models[model_type]

    def get_available_models(self) -> List[ModelType]:
        """Get list of available models"""
        return list(self.loaded_models.keys())

    async def switch_model(self, model_type: ModelType):
        """Switch active model for inference"""
        if model_type not in self.loaded_models:
            logger.warning(f"Model {model_type.value} not loaded, loading now...")
            config = self.model_configs[model_type]
            await self._load_model(model_type, config)

        logger.info(f"Switched to model: {model_type.value}")

    async def get_model_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for loaded models"""
        metrics = {}

        for model_type, model_data in self.loaded_models.items():
            model_metrics = {
                "type": model_data["type"],
                "config": model_data["config"].__dict__,
                "loaded": True
            }

            # Add model-specific metrics
            if model_data["type"] in ["transformers_cpu", "transformers_gpu", "fine_tuned"]:
                model = model_data["model"]
                model_metrics.update({
                    "parameters": sum(p.numel() for p in model.parameters()),
                    "trainable_parameters": sum(p.numel() for p in model.parameters() if p.requires_grad),
                    "device": str(next(model.parameters()).device)
                })

            metrics[model_type.value] = model_metrics

        return metrics

    async def _mock_download_model(self, model_file: Path):
        """Mock model download - create placeholder file"""
        # In real implementation, this would download from HuggingFace
        model_file.write_text("# Mock GGUF model file\n# Real implementation would download actual model")
        await asyncio.sleep(0.1)  # Simulate download time

    async def unload_model(self, model_type: ModelType):
        """Unload a model to free memory"""
        if model_type in self.loaded_models:
            model_data = self.loaded_models[model_type]

            # Clean up model resources
            if "model" in model_data:
                del model_data["model"]
            if "tokenizer" in model_data:
                del model_data["tokenizer"]

            del self.loaded_models[model_type]

            # Force garbage collection
            import gc
            gc.collect()

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            logger.info(f"Unloaded model: {model_type.value}")

    async def shutdown(self):
        """Shutdown model manager and clean up resources"""
        logger.info("Shutting down ModelManager")

        # Unload all models
        for model_type in list(self.loaded_models.keys()):
            await self.unload_model(model_type)

        logger.info("ModelManager shutdown complete")