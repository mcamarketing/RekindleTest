"""
Training Pipeline API Endpoints
FastAPI routes for managing LLM training cycle

Endpoints:
- POST /training/run - Trigger training cycle manually
- GET /training/status/{job_id} - Get training job status
- GET /training/models - List all models
- POST /training/deploy/{model_id} - Deploy a model
- POST /training/promote-winner - Promote A/B test winner
- GET /training/stats - Get training data statistics
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from supabase import create_client, Client
import os

from .training_orchestrator import TrainingOrchestrator
from .model_registry import ModelRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/training", tags=["LLM Training"])


# Dependency: Get Supabase client
def get_supabase() -> Client:
    """Dependency to get Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    return create_client(supabase_url, supabase_key)


# Dependency: Get Training Orchestrator
def get_orchestrator(supabase: Client = Depends(get_supabase)) -> TrainingOrchestrator:
    """Dependency to get TrainingOrchestrator"""
    return TrainingOrchestrator(
        supabase=supabase,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        output_dir=os.getenv("TRAINING_DATA_DIR", "./training_data"),
    )


# Dependency: Get Model Registry
def get_registry(supabase: Client = Depends(get_supabase)) -> ModelRegistry:
    """Dependency to get ModelRegistry"""
    return ModelRegistry(supabase)


# Request models
class TrainModelRequest(BaseModel):
    organization_id: Optional[str] = None
    model_version: Optional[str] = None
    min_quality_score: float = 0.6
    deploy_immediately: bool = False
    ab_test_percentage: float = 10.0


class DeployModelRequest(BaseModel):
    traffic_percentage: float = 100.0
    ab_test_group: Optional[str] = None


# Endpoints

@router.post("/run")
async def run_training_cycle(
    request: TrainModelRequest,
    orchestrator: TrainingOrchestrator = Depends(get_orchestrator),
):
    """
    Trigger a training cycle manually.

    This will:
    1. Export training data from outcome_labels
    2. Format as GPT-4 JSONL
    3. Upload to OpenAI
    4. Start fine-tuning job
    5. Wait for completion
    6. Register model
    7. (Optional) Deploy with A/B test
    """
    try:
        logger.info("Training cycle triggered via API")

        result = await orchestrator.run_training_cycle(
            organization_id=request.organization_id,
            model_version=request.model_version,
            min_quality_score=request.min_quality_score,
            deploy_immediately=request.deploy_immediately,
            ab_test_percentage=request.ab_test_percentage,
        )

        return result

    except Exception as e:
        logger.error(f"Training cycle failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}")
async def get_training_status(
    job_id: str,
    orchestrator: TrainingOrchestrator = Depends(get_orchestrator),
):
    """Get status of a fine-tuning job"""
    try:
        status = await orchestrator.trainer.get_job_status(job_id)
        return status

    except Exception as e:
        logger.error(f"Failed to get job status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models(
    status: Optional[str] = None,
    organization_id: Optional[str] = None,
    registry: ModelRegistry = Depends(get_registry),
):
    """
    List all models in registry.

    Query params:
    - status: Filter by status (training, ready, deployed, archived, failed)
    - organization_id: Filter by organization
    """
    try:
        if status == "deployed":
            models = await registry.get_deployed_models(
                organization_id=organization_id if organization_id else None
            )
        else:
            # Get all models
            query = registry.supabase.table("model_registry").select("*")

            if status:
                query = query.eq("status", status)

            if organization_id:
                query = query.eq("organization_id", organization_id)

            result = query.order("created_at", desc=True).execute()
            models = result.data

        return {
            "total": len(models),
            "models": models,
        }

    except Exception as e:
        logger.error(f"Failed to list models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy/{registry_id}")
async def deploy_model(
    registry_id: str,
    request: DeployModelRequest,
    registry: ModelRegistry = Depends(get_registry),
):
    """Deploy a model to production"""
    try:
        await registry.deploy_model(
            registry_id=registry_id,
            traffic_percentage=request.traffic_percentage,
            ab_test_group=request.ab_test_group,
        )

        return {
            "status": "success",
            "message": f"Model {registry_id} deployed with {request.traffic_percentage}% traffic",
        }

    except Exception as e:
        logger.error(f"Failed to deploy model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/archive/{registry_id}")
async def archive_model(
    registry_id: str,
    registry: ModelRegistry = Depends(get_registry),
):
    """Archive a model (remove from deployment)"""
    try:
        await registry.archive_model(registry_id=registry_id)

        return {
            "status": "success",
            "message": f"Model {registry_id} archived",
        }

    except Exception as e:
        logger.error(f"Failed to archive model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/promote-winner")
async def promote_ab_test_winner(
    organization_id: Optional[str] = None,
    orchestrator: TrainingOrchestrator = Depends(get_orchestrator),
):
    """
    Promote A/B test winner to 100% traffic.

    Analyzes performance of control vs variant and promotes the winner.
    """
    try:
        result = await orchestrator.promote_ab_test_winner(
            organization_id=organization_id if organization_id else None
        )

        return result

    except Exception as e:
        logger.error(f"Failed to promote winner: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_training_stats(
    organization_id: Optional[str] = None,
    orchestrator: TrainingOrchestrator = Depends(get_orchestrator),
):
    """Get statistics about available training data"""
    try:
        stats = await orchestrator.formatter.get_training_stats(
            organization_id=organization_id
        )

        return stats

    except Exception as e:
        logger.error(f"Failed to get training stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard")
async def get_model_leaderboard(
    min_samples: int = 100,
    registry: ModelRegistry = Depends(get_registry),
):
    """
    Get model performance leaderboard.

    Shows all deployed models ranked by close rate, reply rate, revenue.
    """
    try:
        leaderboard = await registry.get_leaderboard(min_samples=min_samples)

        return {
            "total": len(leaderboard),
            "leaderboard": leaderboard,
        }

    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def training_pipeline_health():
    """Health check for training pipeline"""
    return {
        "status": "healthy",
        "pipeline": "llm_training",
        "components": {
            "data_formatter": "ready",
            "model_trainer": "ready",
            "model_registry": "ready",
            "orchestrator": "ready",
        },
    }
