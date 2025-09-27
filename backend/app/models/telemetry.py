from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql import func
from app.core.database import Base


class TelemetryData(Base):
    __tablename__ = "telemetry_data"
    
    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    fps = Column(Float, nullable=False)
    latency = Column(Float, nullable=False)  # Inference latency in milliseconds
    cpu_usage = Column(Float, nullable=False)  # CPU usage percentage
    gpu_usage = Column(Float, nullable=False)  # GPU usage percentage
    memory_usage = Column(Float, nullable=False)  # Memory usage percentage
    model_inference = Column(JSON, nullable=False)  # Model inference times
    system_info = Column(JSON, nullable=True)  # Additional system information
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TelemetryMetrics(Base):
    __tablename__ = "telemetry_metrics"
    
    id = Column(String, primary_key=True, index=True)
    metric_type = Column(String, nullable=False, index=True)  # fps, latency, cpu_usage, etc.
    time_range = Column(String, nullable=False)  # 1h, 6h, 24h, 7d, 30d
    average = Column(Float, nullable=False)
    min_value = Column(Float, nullable=False)
    max_value = Column(Float, nullable=False)
    median = Column(Float, nullable=False)
    p95 = Column(Float, nullable=False)
    p99 = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
