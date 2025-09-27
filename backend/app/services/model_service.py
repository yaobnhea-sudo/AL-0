import os
import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.model import Model, ModelMetrics
from app.schemas.model import ModelCreate, ModelUpdate, ModelType, ModelStatus
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self):
        self.loaded_models: Dict[str, Any] = {}
        self.model_cache_dir = settings.MODEL_CACHE_DIR
    
    async def initialize(self):
        """Initialize the model service"""
        logger.info("Initializing model service...")
        
        # Ensure model cache directory exists
        os.makedirs(self.model_cache_dir, exist_ok=True)
        
        # Load available models from disk
        await self.refresh_models()
        
        logger.info("Model service initialized")
    
    async def get_models(
        self, 
        db: Session, 
        model_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Model]:
        """Get list of models with optional filtering"""
        query = db.query(Model)
        
        if model_type:
            query = query.filter(Model.type == model_type)
        if status:
            query = query.filter(Model.status == status)
        
        return query.offset(offset).limit(limit).all()
    
    async def get_model(self, db: Session, model_id: str) -> Optional[Model]:
        """Get a specific model by ID"""
        return db.query(Model).filter(Model.id == model_id).first()
    
    async def create_model(self, db: Session, model_data: ModelCreate) -> Model:
        """Create a new model"""
        model = Model(
            id=f"model_{len(db.query(Model).all()) + 1}",
            **model_data.dict()
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model
    
    async def update_model(self, db: Session, model_id: str, model_data: ModelUpdate) -> Optional[Model]:
        """Update an existing model"""
        model = await self.get_model(db, model_id)
        if not model:
            return None
        
        update_data = model_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        
        db.commit()
        db.refresh(model)
        return model
    
    async def delete_model(self, db: Session, model_id: str) -> bool:
        """Delete a model"""
        model = await self.get_model(db, model_id)
        if not model:
            return False
        
        # Unload model if it's loaded
        if model_id in self.loaded_models:
            await self.unload_model(model_id)
        
        db.delete(model)
        db.commit()
        return True
    
    async def load_model(self, model_id: str) -> bool:
        """Load a model into memory"""
        try:
            # For demo purposes, simulate model loading
            logger.info(f"Loading model {model_id}...")
            
            # Simulate loading time
            await asyncio.sleep(1)
            
            # Mark model as loaded
            self.loaded_models[model_id] = {
                "loaded_at": asyncio.get_event_loop().time(),
                "status": "loaded"
            }
            
            logger.info(f"Model {model_id} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return False
    
    async def unload_model(self, model_id: str) -> bool:
        """Unload a model from memory"""
        try:
            if model_id in self.loaded_models:
                del self.loaded_models[model_id]
                logger.info(f"Model {model_id} unloaded")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unload model {model_id}: {e}")
            return False
    
    async def get_model_status(self, model_id: str) -> str:
        """Get the current status of a model"""
        if model_id in self.loaded_models:
            return "loaded"
        return "unloaded"
    
    async def get_model_metrics(self, db: Session, model_id: str) -> Optional[ModelMetrics]:
        """Get performance metrics for a model"""
        return db.query(ModelMetrics).filter(ModelMetrics.model_id == model_id).first()
    
    async def refresh_models(self, db: Session):
        """Refresh the model registry by scanning for new models"""
        logger.info("Refreshing model registry...")
        
        # For demo purposes, create some sample models
        sample_models = [
            {
                "id": "yolov8n",
                "name": "YOLOv8 Nano",
                "type": "detection",
                "description": "Ultra-fast object detection model",
                "version": "8.0.0",
                "framework": "onnx",
                "status": "active",
                "accuracy": 0.85,
                "latency": 8.5,
                "size": "6.2MB"
            },
            {
                "id": "yolov8s",
                "name": "YOLOv8 Small",
                "type": "detection",
                "description": "Balanced speed and accuracy",
                "version": "8.0.0",
                "framework": "onnx",
                "status": "active",
                "accuracy": 0.89,
                "latency": 12.3,
                "size": "21.5MB"
            },
            {
                "id": "deeplabv3",
                "name": "DeepLabV3",
                "type": "segmentation",
                "description": "High-accuracy semantic segmentation",
                "version": "3.0.0",
                "framework": "onnx",
                "status": "active",
                "accuracy": 0.92,
                "latency": 45.2,
                "size": "156MB"
            },
            {
                "id": "pointpillars",
                "name": "PointPillars",
                "type": "lidar",
                "description": "3D object detection from LIDAR",
                "version": "1.0.0",
                "framework": "onnx",
                "status": "active",
                "accuracy": 0.88,
                "latency": 25.7,
                "size": "89MB"
            }
        ]
        
        for model_data in sample_models:
            existing_model = await self.get_model(db, model_data["id"])
            if not existing_model:
                model = Model(**model_data)
                db.add(model)
        
        db.commit()
        logger.info("Model registry refreshed")
    
    async def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded model IDs"""
        return list(self.loaded_models.keys())
    
    async def is_model_loaded(self, model_id: str) -> bool:
        """Check if a model is currently loaded"""
        return model_id in self.loaded_models
