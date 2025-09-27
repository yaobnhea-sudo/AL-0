from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DatasetType(str, Enum):
    DETECTION = "detection"
    SEGMENTATION = "segmentation"
    LIDAR = "lidar"
    MULTIMODAL = "multimodal"


class Dataset(BaseModel):
    id: str = Field(..., description="Dataset ID")
    name: str = Field(..., description="Dataset name")
    description: str = Field(..., description="Dataset description")
    type: DatasetType = Field(..., description="Dataset type")
    size: str = Field(..., description="Dataset size")
    samples: int = Field(..., description="Number of samples")
    classes: List[str] = Field(..., description="List of class names")
    format: str = Field(..., description="Data format")
    license: str = Field(..., description="Dataset license")
    download_url: str = Field(..., description="Download URL")
    documentation: str = Field(..., description="Documentation URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class DatasetStats(BaseModel):
    dataset_id: str = Field(..., description="Dataset ID")
    total_samples: int = Field(..., description="Total number of samples")
    class_distribution: Dict[str, int] = Field(..., description="Distribution of classes")
    average_image_size: Dict[str, float] = Field(..., description="Average image dimensions")
    file_size_distribution: Dict[str, int] = Field(..., description="File size distribution")
    quality_metrics: Dict[str, float] = Field(..., description="Quality metrics")
    last_updated: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class DatasetSample(BaseModel):
    id: str = Field(..., description="Sample ID")
    dataset_id: str = Field(..., description="Dataset ID")
    file_path: str = Field(..., description="File path")
    file_size: int = Field(..., description="File size in bytes")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")
    classes: List[str] = Field(..., description="Sample classes")
    annotations: Optional[Dict[str, Any]] = Field(None, description="Sample annotations")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class DatasetResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Optional[Dataset] = Field(None, description="Dataset data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class DatasetListResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: List[Dataset] = Field(..., description="List of datasets")
    total: int = Field(..., description="Total number of datasets")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class DatasetStatsResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Optional[DatasetStats] = Field(None, description="Dataset statistics")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class DatasetDownloadResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    download_url: str = Field(..., description="Download URL")
    expires_at: str = Field(..., description="Download URL expiration time")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class DatasetSamplesResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: List[DatasetSample] = Field(..., description="Dataset samples")
    dataset_id: str = Field(..., description="Dataset ID")
    limit: int = Field(..., description="Number of samples per page")
    offset: int = Field(..., description="Number of samples skipped")
    total: int = Field(..., description="Total number of samples")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")
