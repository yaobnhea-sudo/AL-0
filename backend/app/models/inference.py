from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class InferenceJob(Base):
    __tablename__ = "inference_jobs"
    
    id = Column(String, primary_key=True, index=True)
    model_id = Column(String, nullable=False, index=True)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)  # image, video
    status = Column(String, nullable=False, default="pending")  # pending, processing, completed, failed, cancelled
    confidence_threshold = Column(Float, nullable=False, default=0.5)
    result = Column(JSON, nullable=True)  # Inference results
    error_message = Column(Text, nullable=True)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class InferenceResult(Base):
    __tablename__ = "inference_results"
    
    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("inference_jobs.id"), nullable=False, index=True)
    frame_number = Column(Integer, nullable=True)  # For video inference
    result_type = Column(String, nullable=False)  # detection, segmentation
    result_data = Column(JSON, nullable=False)  # Actual inference result
    inference_time = Column(Float, nullable=False)  # Inference time in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    job = relationship("InferenceJob", back_populates="results")


# Add relationship to InferenceJob
InferenceJob.results = relationship("InferenceResult", back_populates="job")
