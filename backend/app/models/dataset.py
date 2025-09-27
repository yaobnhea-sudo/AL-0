from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False, index=True)  # detection, segmentation, lidar, multimodal
    size = Column(String, nullable=False)  # e.g., "15 GB", "1.2 TB"
    samples = Column(Integer, nullable=False)
    classes = Column(JSON, nullable=True)  # List of class names
    format = Column(String, nullable=False)  # e.g., "PNG, PCL", "JPG, PCD"
    license = Column(String, nullable=False)
    download_url = Column(String, nullable=False)
    documentation = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DatasetStats(Base):
    __tablename__ = "dataset_stats"
    
    id = Column(String, primary_key=True, index=True)
    dataset_id = Column(String, nullable=False, index=True)
    total_samples = Column(Integer, nullable=False)
    class_distribution = Column(JSON, nullable=True)  # Dict of class -> count
    average_image_size = Column(JSON, nullable=True)  # Dict with width, height
    file_size_distribution = Column(JSON, nullable=True)  # Dict of size category -> count
    quality_metrics = Column(JSON, nullable=True)  # Dict of quality metrics
    last_updated = Column(DateTime(timezone=True), server_default=func.now())


class DatasetSample(Base):
    __tablename__ = "dataset_samples"
    
    id = Column(String, primary_key=True, index=True)
    dataset_id = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    classes = Column(JSON, nullable=True)  # List of classes in this sample
    annotations = Column(JSON, nullable=True)  # Sample annotations
    created_at = Column(DateTime(timezone=True), server_default=func.now())
