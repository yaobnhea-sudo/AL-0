from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import asyncio

from app.core.database import get_db
from app.services.model_optimization import ModelOptimizer
from app.services.monitoring_service import monitoring_service

router = APIRouter()


@router.post("/optimize/{model_id}")
async def optimize_model(
    model_id: str,
    optimization_level: str = "basic",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Optimize a model for better performance"""
    try:
        # Get model service from app state
        # This would be injected in a real implementation
        model_optimizer = ModelOptimizer()
        
        # Find model file (simplified for demo)
        model_path = f"./models/{model_id}.onnx"
        
        # Optimize model in background
        background_tasks.add_task(
            model_optimizer.optimize_model,
            model_path,
            optimization_level
        )
        
        return {
            "success": True,
            "message": f"Model {model_id} optimization started",
            "optimization_level": optimization_level
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quantize/{model_id}")
async def quantize_model(
    model_id: str,
    quantization_type: str = "dynamic",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Quantize a model for edge deployment"""
    try:
        model_optimizer = ModelOptimizer()
        
        # Find model file
        model_path = f"./models/{model_id}.onnx"
        
        # Quantize model in background
        background_tasks.add_task(
            model_optimizer.quantize_model,
            model_path,
            quantization_type
        )
        
        return {
            "success": True,
            "message": f"Model {model_id} quantization started",
            "quantization_type": quantization_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark/{model_id}")
async def benchmark_model(
    model_id: str,
    input_shape: str = "640,640,3",
    num_runs: int = 100,
    db: Session = Depends(get_db)
):
    """Benchmark model performance"""
    try:
        model_optimizer = ModelOptimizer()
        
        # Parse input shape
        shape_parts = input_shape.split(',')
        input_shape_tuple = tuple(int(x) for x in shape_parts)
        
        # Find model file
        model_path = f"./models/{model_id}.onnx"
        
        # Benchmark model
        stats = await model_optimizer.benchmark_model(
            model_path,
            input_shape_tuple,
            num_runs
        )
        
        return {
            "success": True,
            "data": stats,
            "model_id": model_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/{model_id}")
async def compare_models(
    model_id: str,
    original_path: str,
    optimized_path: str,
    input_shape: str = "640,640,3",
    db: Session = Depends(get_db)
):
    """Compare original and optimized model performance"""
    try:
        model_optimizer = ModelOptimizer()
        
        # Parse input shape
        shape_parts = input_shape.split(',')
        input_shape_tuple = tuple(int(x) for x in shape_parts)
        
        # Compare models
        comparison = await model_optimizer.compare_models(
            original_path,
            optimized_path,
            input_shape_tuple
        )
        
        return {
            "success": True,
            "data": comparison,
            "model_id": model_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{model_id}")
async def get_model_info(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed model information"""
    try:
        model_optimizer = ModelOptimizer()
        
        # Find model file
        model_path = f"./models/{model_id}.onnx"
        
        # Get model info
        info = await model_optimizer.get_model_info(model_path)
        
        return {
            "success": True,
            "data": info,
            "model_id": model_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/{model_id}")
async def validate_model(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Validate model integrity and performance"""
    try:
        model_optimizer = ModelOptimizer()
        
        # Find model file
        model_path = f"./models/{model_id}.onnx"
        
        # Validate model
        validation = await model_optimizer.validate_model(model_path)
        
        return {
            "success": True,
            "data": validation,
            "model_id": model_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
