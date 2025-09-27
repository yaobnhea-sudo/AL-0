from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Model(Base):
    __tablename__ = "models"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # detection, segmentation, lidar, prediction
    description = Column(Text, nullable=True)
    version = Column(String, nullable=False)
    framework = Column(String, nullable=False)  # pytorch, onnx, tensorflow
    status = Column(String, nullable=False, default="active")  # active, training, deprecated
    accuracy = Column(Float, nullable=False, default=0.0)
    latency = Column(Float, nullable=False, default=0.0)
    size = Column(String, nullable=False)  # e.g., "50MB", "1.2GB"
    file_path = Column(String, nullable=True)  # Path to model file
    config = Column(JSON, nullable=True)  # Model configuration
    is_loaded = Column(Boolean, default=False)  # Whether model is loaded in memory
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ModelMetrics(Base):
    __tablename__ = "model_metrics"
    
    id = Column(String, primary_key=True, index=True)
    model_id = Column(String, nullable=False, index=True)
    mAP = Column(Float, nullable=False)
    IoU = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    confusion_matrix = Column(JSON, nullable=True)
    dataset_name = Column(String, nullable=True)
    evaluation_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
