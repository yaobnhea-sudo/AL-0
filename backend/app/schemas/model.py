from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ModelType(str, Enum):
    DETECTION = "detection"
    SEGMENTATION = "segmentation"
    LIDAR = "lidar"
    PREDICTION = "prediction"


class ModelStatus(str, Enum):
    ACTIVE = "active"
    TRAINING = "training"
    DEPRECATED = "deprecated"


class ModelBase(BaseModel):
    name: str = Field(..., description="Model name")
    type: ModelType = Field(..., description="Model type")
    description: str = Field(..., description="Model description")
    version: str = Field(..., description="Model version")
    framework: str = Field(..., description="ML framework used")
    status: ModelStatus = Field(..., description="Model status")


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ModelStatus] = None


class Model(ModelBase):
    id: str = Field(..., description="Model ID")
    accuracy: float = Field(..., description="Model accuracy (0-1)")
    latency: float = Field(..., description="Inference latency in milliseconds")
    size: str = Field(..., description="Model size")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ModelMetrics(BaseModel):
    model_id: str = Field(..., description="Model ID")
    mAP: float = Field(..., description="Mean Average Precision")
    IoU: float = Field(..., description="Intersection over Union")
    precision: float = Field(..., description="Precision score")
    recall: float = Field(..., description="Recall score")
    f1_score: float = Field(..., description="F1 score")
    confusion_matrix: List[List[int]] = Field(..., description="Confusion matrix")
    created_at: datetime = Field(..., description="Metrics timestamp")
    
    class Config:
        from_attributes = True


class ModelResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Optional[Model] = Field(None, description="Model data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class ModelListResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: List[Model] = Field(..., description="List of models")
    total: int = Field(..., description="Total number of models")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class ModelMetricsResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Optional[ModelMetrics] = Field(None, description="Model metrics data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class ModelStatusResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    model_id: str = Field(..., description="Model ID")
    status: str = Field(..., description="Model status")
    loaded: bool = Field(..., description="Whether model is loaded in memory")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")
