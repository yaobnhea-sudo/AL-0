from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from sqlalchemy.orm import Session
import asyncio

from app.core.database import get_db
from app.services.model_service import ModelService
from app.models.model import Model, ModelMetrics
from app.schemas.model import ModelResponse, ModelMetricsResponse, ModelListResponse

router = APIRouter()


@router.get("/models", response_model=ModelListResponse)
async def get_models(
    model_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of available models with optional filtering"""
    try:
        model_service = ModelService()
        models = await model_service.get_models(
            db=db,
            model_type=model_type,
            status=status
        )
        
        return ModelListResponse(
            success=True,
            data=models,
            total=len(models)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific model"""
    try:
        model_service = ModelService()
        model = await model_service.get_model(db=db, model_id=model_id)
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return ModelResponse(success=True, data=model)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}/metrics", response_model=ModelMetricsResponse)
async def get_model_metrics(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Get performance metrics for a specific model"""
    try:
        model_service = ModelService()
        metrics = await model_service.get_model_metrics(db=db, model_id=model_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Model metrics not found")
        
        return ModelMetricsResponse(success=True, data=metrics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/load")
async def load_model(
    model_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Load a model into memory for inference"""
    try:
        model_service = ModelService()
        
        # Check if model exists
        model = await model_service.get_model(db=db, model_id=model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Load model in background
        background_tasks.add_task(model_service.load_model, model_id)
        
        return {
            "success": True,
            "message": f"Model {model_id} is being loaded",
            "model_id": model_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/unload")
async def unload_model(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Unload a model from memory"""
    try:
        model_service = ModelService()
        success = await model_service.unload_model(model_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Model not found or not loaded")
        
        return {
            "success": True,
            "message": f"Model {model_id} has been unloaded",
            "model_id": model_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}/status")
async def get_model_status(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Get the current status of a model (loaded/unloaded)"""
    try:
        model_service = ModelService()
        status = await model_service.get_model_status(model_id)
        
        return {
            "success": True,
            "model_id": model_id,
            "status": status,
            "loaded": status == "loaded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/refresh")
async def refresh_models(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Refresh the model registry by scanning for new models"""
    try:
        model_service = ModelService()
        
        # Refresh models in background
        background_tasks.add_task(model_service.refresh_models, db)
        
        return {
            "success": True,
            "message": "Model registry refresh initiated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
