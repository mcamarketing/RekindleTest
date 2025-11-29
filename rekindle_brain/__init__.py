"""
Rekindle Brain - Autonomous Business Intelligence LLM

A specialized language model for business strategy, marketing, sales, and negotiation.
"""

from .brain import RekindleBrain
from .config import BrainConfig
from .models import ModelManager
from .training import BrainTrainer
from .inference import BrainInference
from .data import DataPipeline
from .security import SecurityManager

__version__ = "0.1.0"
__author__ = "Rekindle.ai"

__all__ = [
    "RekindleBrain",
    "BrainConfig",
    "ModelManager",
    "BrainTrainer",
    "BrainInference",
    "DataPipeline",
    "SecurityManager"
]