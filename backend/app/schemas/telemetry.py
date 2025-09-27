from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TelemetryData(BaseModel):
    timestamp: datetime = Field(..., description="Telemetry timestamp")
    fps: float = Field(..., description="Frames per second")
    latency: float = Field(..., description="Inference latency in milliseconds")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    gpu_usage: float = Field(..., description="GPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    model_inference: Dict[str, float] = Field(..., description="Model inference times")
    
    class Config:
        from_attributes = True


class TelemetryMetrics(BaseModel):
    metric_type: str = Field(..., description="Type of metric")
    average: float = Field(..., description="Average value")
    min_value: float = Field(..., description="Minimum value")
    max_value: float = Field(..., description="Maximum value")
    median: float = Field(..., description="Median value")
    p95: float = Field(..., description="95th percentile")
    p99: float = Field(..., description="99th percentile")
    count: int = Field(..., description="Number of data points")
    time_range: str = Field(..., description="Time range for metrics")
    
    class Config:
        from_attributes = True


class TelemetryDataResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Optional[TelemetryData] = Field(None, description="Current telemetry data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class TelemetryHistoryResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: List[TelemetryData] = Field(..., description="Historical telemetry data")
    start_time: Optional[str] = Field(None, description="Start time for data range")
    end_time: Optional[str] = Field(None, description="End time for data range")
    total: int = Field(..., description="Total number of data points")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class TelemetryMetricsResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: List[TelemetryMetrics] = Field(..., description="Telemetry metrics")
    time_range: str = Field(..., description="Time range for metrics")
    start_time: str = Field(..., description="Start time for metrics")
    end_time: str = Field(..., description="End time for metrics")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class TelemetryHealthResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    status: str = Field(..., description="System health status")
    active_connections: int = Field(..., description="Number of active WebSocket connections")
    timestamp: str = Field(..., description="Health check timestamp")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")
