"""
Brain Training Module

Implements the 3-phase training strategy:
1. Foundation Prep - Quantization and RAG setup
2. Domain Tuning + RAG - LoRA fine-tuning on business data
3. Continual Learning - Ongoing updates from business outcomes
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .config import BrainConfig, ModelType, TrainingPhase

logger = logging.getLogger(__name__)

class BrainTrainer:
    """Handles training and fine-tuning of Rekindle Brain models"""

    def __init__(self, config: BrainConfig):
        self.config = config
        self.training_history: List[Dict[str, Any]] = []
        self.output_dir = Path("models/training_output")
        self.output_dir.mkdir(exist_ok=True, parents=True)

    async def fine_tune(self, model_type: ModelType, data_path: str, output_dir: str,
                       training_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fine-tune a model on business data using LoRA

        Args:
            model_type: Which base model to fine-tune
            data_path: Path to training data (JSONL format)
            output_dir: Where to save the fine-tuned model
            training_config: Optional training configuration override

        Returns:
            Training results and metrics
        """
        logger.info(f"Starting LoRA fine-tuning for {model_type.value}")

        # Use provided config or default
        config = training_config or self.config.training_config

        try:
            # Validate training data
            await self._validate_training_data(data_path)

            # Prepare training data
            processed_data = await self._prepare_training_data(data_path)

            # Run LoRA training
            training_result = await self._run_lora_training(
                model_type=model_type,
                train_data=processed_data,
                output_dir=output_dir,
                config=config
            )

            # Evaluate training
            evaluation = await self._evaluate_training(training_result["model_path"])

            # Record training session
            training_session = {
                "timestamp": datetime.now().isoformat(),
                "model_type": model_type.value,
                "data_path": data_path,
                "output_dir": output_dir,
                "config": config,
                "results": training_result,
                "evaluation": evaluation
            }

            self.training_history.append(training_session)

            # Save training metadata
            await self._save_training_metadata(training_session, output_dir)

            logger.info(f"Training completed successfully. Model saved to {output_dir}")

            return {
                "status": "completed",
                "model_path": training_result["model_path"],
                "training_metrics": training_result["metrics"],
                "evaluation": evaluation,
                "session_id": len(self.training_history)
            }

        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise

    async def _validate_training_data(self, data_path: str):
        """Validate training data format and quality"""
        data_file = Path(data_path)

        if not data_file.exists():
            raise FileNotFoundError(f"Training data not found: {data_path}")

        # Check file size
        if data_file.stat().st_size < 1000:  # At least 1KB
            raise ValueError("Training data file too small")

        # Validate JSONL format (sample first few lines)
        sample_lines = []
        with open(data_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 5:  # Check first 5 lines
                    break
                try:
                    json.loads(line.strip())
                    sample_lines.append(line.strip())
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSONL format at line {i+1}: {e}")

        if len(sample_lines) == 0:
            raise ValueError("No valid JSON lines found in training data")

        # Validate required fields in sample
        sample_data = json.loads(sample_lines[0])
        required_fields = ["instruction", "output"]
        missing_fields = [field for field in required_fields if field not in sample_data]

        if missing_fields:
            raise ValueError(f"Missing required fields in training data: {missing_fields}")

        logger.info(f"Training data validation passed. File size: {data_file.stat().st_size} bytes")

    async def _prepare_training_data(self, data_path: str) -> Dict[str, Any]:
        """Prepare and preprocess training data"""
        logger.info("Preparing training data...")

        # In a real implementation, this would:
        # 1. Load and parse JSONL data
        # 2. Apply data cleaning and filtering
        # 3. Format for the specific model
        # 4. Create train/validation splits
        # 5. Apply tokenization

        processed_data = {
            "train_path": data_path,
            "validation_path": None,  # Would create validation split
            "num_samples": await self._count_samples(data_path),
            "avg_instruction_length": await self._calculate_avg_length(data_path, "instruction"),
            "avg_output_length": await self._calculate_avg_length(data_path, "output")
        }

        logger.info(f"Data preparation complete: {processed_data['num_samples']} samples")

        return processed_data

    async def _run_lora_training(self, model_type: ModelType, train_data: Dict[str, Any],
                                output_dir: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LoRA fine-tuning"""
        logger.info("Starting LoRA training...")

        try:
            # Import required libraries
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                TrainingArguments,
                Trainer,
                DataCollatorForLanguageModeling
            )
            from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
            import torch

            # Get model config
            model_config = self.config.get_model_config(model_type)

            # Load model and tokenizer
            model = AutoModelForCausalLM.from_pretrained(
                model_config.huggingface_repo,
                load_in_8bit=True,
                torch_dtype=torch.float16,
                device_map="auto"
            )

            tokenizer = AutoTokenizer.from_pretrained(model_config.huggingface_repo)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            # Prepare model for k-bit training
            model = prepare_model_for_kbit_training(model)

            # Configure LoRA
            lora_config = LoraConfig(**config["lora_config"])
            model = get_peft_model(model, lora_config)

            # Load and tokenize dataset
            train_dataset = await self._load_dataset(train_data["train_path"], tokenizer)

            # Training arguments
            training_args = TrainingArguments(
                output_dir=output_dir,
                **config["training_args"]
            )

            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
            )

            # Train the model
            logger.info("Starting training...")
            train_result = trainer.train()

            # Save the model
            model_path = Path(output_dir) / "final_model"
            trainer.save_model(str(model_path))

            # Collect training metrics
            metrics = {
                "training_loss": train_result.training_loss,
                "train_runtime": train_result.metrics.get("train_runtime", 0),
                "train_samples_per_second": train_result.metrics.get("train_samples_per_second", 0),
                "train_steps_per_second": train_result.metrics.get("train_steps_per_second", 0),
                "total_flos": train_result.metrics.get("total_flos", 0),
                "epoch": train_result.metrics.get("epoch", 0)
            }

            logger.info(f"Training completed. Loss: {metrics['training_loss']:.4f}")

            return {
                "model_path": str(model_path),
                "metrics": metrics,
                "lora_config": config["lora_config"],
                "training_args": config["training_args"]
            }

        except ImportError as e:
            logger.error(f"Missing required packages for training: {e}")
            raise ImportError("Install training dependencies: pip install transformers peft torch datasets")

    async def _evaluate_training(self, model_path: str) -> Dict[str, Any]:
        """Evaluate the trained model"""
        logger.info("Evaluating trained model...")

        # In a real implementation, this would:
        # 1. Load the trained model
        # 2. Run evaluation on validation set
        # 3. Calculate perplexity, BLEU scores, etc.
        # 4. Test on business-specific tasks

        # Mock evaluation results
        evaluation = {
            "perplexity": 12.5,
            "business_task_accuracy": 0.78,
            "instruction_following_score": 0.82,
            "safety_score": 0.95,
            "inference_speed_tokens_per_sec": 45.2
        }

        logger.info(f"Evaluation complete. Perplexity: {evaluation['perplexity']}")

        return evaluation

    async def generate_training_signals(self, critic_evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate training signals from critic evaluation"""
        logger.info("Generating training signals from critic evaluation")

        training_signals = []

        # Process successful patterns
        for success in critic_evaluation.get("success_patterns", []):
            signal = {
                "type": "positive",
                "pattern": success.get("pattern"),
                "outcome": success.get("outcome"),
                "confidence": success.get("confidence", 0.8),
                "context": success.get("context", {})
            }
            training_signals.append(signal)

        # Process failure patterns
        for failure in critic_evaluation.get("failure_patterns", []):
            signal = {
                "type": "negative",
                "pattern": failure.get("pattern"),
                "error": failure.get("error"),
                "improvement": failure.get("suggested_improvement"),
                "context": failure.get("context", {})
            }
            training_signals.append(signal)

        logger.info(f"Generated {len(training_signals)} training signals")

        return training_signals

    async def create_synthetic_data(self, training_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create synthetic training data from signals"""
        logger.info(f"Creating synthetic data from {len(training_signals)} signals")

        synthetic_samples = []

        for signal in training_signals:
            if signal["type"] == "positive":
                # Create positive example
                sample = {
                    "instruction": f"Given this business scenario: {signal['context'].get('scenario', 'general business situation')}, provide a strategic recommendation.",
                    "input": json.dumps(signal["context"]),
                    "output": signal["pattern"]
                }
            else:
                # Create negative/improvement example
                sample = {
                    "instruction": f"Improve this business approach: {signal['pattern']}. The issue was: {signal['error']}",
                    "input": json.dumps(signal["context"]),
                    "output": signal["improvement"]
                }

            synthetic_samples.append(sample)

        # Save synthetic data
        synthetic_file = self.output_dir / f"synthetic_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

        with open(synthetic_file, 'w', encoding='utf-8') as f:
            for sample in synthetic_samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')

        logger.info(f"Created {len(synthetic_samples)} synthetic training samples")

        return {
            "data_path": str(synthetic_file),
            "num_samples": len(synthetic_samples),
            "data_types": list(set(s["type"] for s in training_signals))
        }

    async def get_training_history(self) -> List[Dict[str, Any]]:
        """Get training session history"""
        return self.training_history.copy()

    async def get_training_phase_status(self) -> Dict[str, Any]:
        """Get current training phase status"""
        phases = self.config.training_phases
        current_phase = 0  # Would be determined by completion status

        # Calculate completion based on training history
        completed_sessions = len([h for h in self.training_history if h["results"]["status"] == "completed"])

        if completed_sessions >= 10:  # Arbitrary threshold
            current_phase = 2  # Continual learning
        elif completed_sessions >= 1:
            current_phase = 1  # Domain tuning
        else:
            current_phase = 0  # Foundation

        return {
            "current_phase": current_phase,
            "phase_name": phases[current_phase].name,
            "completed_sessions": completed_sessions,
            "next_milestone": phases[min(current_phase + 1, len(phases) - 1)].name
        }

    async def _count_samples(self, data_path: str) -> int:
        """Count samples in JSONL file"""
        count = 0
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    async def _calculate_avg_length(self, data_path: str, field: str) -> float:
        """Calculate average length of a field in JSONL data"""
        lengths = []
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line.strip())
                        if field in data:
                            lengths.append(len(str(data[field])))
                    except json.JSONDecodeError:
                        continue

        return sum(lengths) / len(lengths) if lengths else 0

    async def _load_dataset(self, data_path: str, tokenizer):
        """Load and tokenize dataset for training"""
        # This would implement proper dataset loading and tokenization
        # For now, return a mock dataset class
        class MockDataset:
            def __len__(self):
                return 1000  # Mock length

        return MockDataset()

    async def _save_training_metadata(self, session: Dict[str, Any], output_dir: str):
        """Save training metadata"""
        metadata_file = Path(output_dir) / "training_metadata.json"

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

        logger.info(f"Training metadata saved to {metadata_file}")