from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SimulationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationConfig(BaseModel):
    scenario: str = Field(..., description="Simulation scenario")
    weather: str = Field(..., description="Weather conditions")
    time_of_day: str = Field(..., description="Time of day")
    traffic: str = Field(..., description="Traffic density")
    models: List[str] = Field(..., description="List of model IDs to use")
    duration: Optional[int] = Field(None, description="Simulation duration in seconds")
    max_speed: Optional[float] = Field(None, description="Maximum vehicle speed")
    spawn_rate: Optional[float] = Field(None, description="Vehicle spawn rate")


class SimulationRun(BaseModel):
    id: str = Field(..., description="Simulation run ID")
    name: str = Field(..., description="Simulation name")
    status: SimulationStatus = Field(..., description="Simulation status")
    config: SimulationConfig = Field(..., description="Simulation configuration")
    start_time: Optional[datetime] = Field(None, description="Simulation start time")
    end_time: Optional[datetime] = Field(None, description="Simulation end time")
    duration: Optional[int] = Field(None, description="Simulation duration in seconds")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class SimulationConfigRequest(BaseModel):
    name: str = Field(..., description="Simulation name")
    config: SimulationConfig = Field(..., description="Simulation configuration")


class SimulationConfigResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Optional[SimulationConfig] = Field(None, description="Simulation configuration")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class SimulationRunResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Optional[SimulationRun] = Field(None, description="Simulation run data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class SimulationRunListResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: List[SimulationRun] = Field(..., description="List of simulation runs")
    total: int = Field(..., description="Total number of simulation runs")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class SimulationData(BaseModel):
    timestamp: datetime = Field(..., description="Data timestamp")
    run_id: str = Field(..., description="Simulation run ID")
    frame_number: int = Field(..., description="Frame number")
    camera_data: Optional[Dict[str, Any]] = Field(None, description="Camera sensor data")
    lidar_data: Optional[Dict[str, Any]] = Field(None, description="LIDAR sensor data")
    detections: Optional[List[Dict[str, Any]]] = Field(None, description="Object detections")
    vehicle_state: Optional[Dict[str, Any]] = Field(None, description="Vehicle state")
    environment_state: Optional[Dict[str, Any]] = Field(None, description="Environment state")
    
    class Config:
        from_attributes = True


class SimulationDataResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: List[SimulationData] = Field(..., description="Simulation data")
    run_id: str = Field(..., description="Simulation run ID")
    total: int = Field(..., description="Total number of data points")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")
