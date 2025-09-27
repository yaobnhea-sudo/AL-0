from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class DetectionBox(BaseModel):
    x: float = Field(..., description="Bounding box x coordinate")
    y: float = Field(..., description="Bounding box y coordinate")
    width: float = Field(..., description="Bounding box width")
    height: float = Field(..., description="Bounding box height")
    confidence: float = Field(..., description="Detection confidence (0-1)")
    class_name: str = Field(..., description="Detected class name")
    class_id: int = Field(..., description="Detected class ID")


class SegmentationMask(BaseModel):
    data: List[List[int]] = Field(..., description="Segmentation mask data")
    width: int = Field(..., description="Mask width")
    height: int = Field(..., description="Mask height")
    classes: List[str] = Field(..., description="Class names")
    colors: List[str] = Field(..., description="Class colors")


class DetectionResult(BaseModel):
    boxes: List[DetectionBox] = Field(..., description="Detection bounding boxes")
    image_width: int = Field(..., description="Original image width")
    image_height: int = Field(..., description="Original image height")
    inference_time: float = Field(..., description="Inference time in milliseconds")
    model: str = Field(..., description="Model used for inference")


class SegmentationResult(BaseModel):
    mask: SegmentationMask = Field(..., description="Segmentation mask")
    image_width: int = Field(..., description="Original image width")
    image_height: int = Field(..., description="Original image height")
    inference_time: float = Field(..., description="Inference time in milliseconds")
    model: str = Field(..., description="Model used for inference")


class ImageInferenceRequest(BaseModel):
    model_id: str = Field(..., description="Model ID to use for inference")
    confidence_threshold: float = Field(0.5, description="Confidence threshold for detections")
    max_detections: Optional[int] = Field(None, description="Maximum number of detections")


class ImageInferenceResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Optional[Union[DetectionResult, SegmentationResult]] = Field(None, description="Inference result")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class VideoInferenceRequest(BaseModel):
    model_id: str = Field(..., description="Model ID to use for inference")
    confidence_threshold: float = Field(0.5, description="Confidence threshold for detections")
    frame_skip: int = Field(1, description="Process every Nth frame")
    max_frames: Optional[int] = Field(None, description="Maximum number of frames to process")


class VideoInferenceResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    job_id: str = Field(..., description="Inference job ID")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class InferenceJobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InferenceJob(BaseModel):
    job_id: str = Field(..., description="Job ID")
    model_id: str = Field(..., description="Model ID")
    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., description="File size in bytes")
    status: InferenceJobStatus = Field(..., description="Job status")
    created_at: datetime = Field(..., description="Job creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    result: Optional[Union[List[DetectionResult], List[SegmentationResult]]] = Field(None, description="Inference results")
    error: Optional[str] = Field(None, description="Error message if failed")
    progress: float = Field(0.0, description="Job progress (0-1)")


class InferenceJobResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    job_id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status")
    result: Optional[Union[List[DetectionResult], List[SegmentationResult]]] = Field(None, description="Inference results")
    error: Optional[str] = Field(None, description="Error message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    message: Optional[str] = Field(None, description="Response message")


class InferenceJobListResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: List[InferenceJob] = Field(..., description="List of inference jobs")
    total: int = Field(..., description="Total number of jobs")
    limit: int = Field(..., description="Number of jobs per page")
    offset: int = Field(..., description="Number of jobs skipped")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")
