from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql import func
from app.core.database import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")  # pending, running, paused, stopped, completed, failed
    config = Column(JSON, nullable=False)  # Simulation configuration
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SimulationData(Base):
    __tablename__ = "simulation_data"
    
    id = Column(String, primary_key=True, index=True)
    run_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    frame_number = Column(Integer, nullable=False)
    data_type = Column(String, nullable=False)  # camera, lidar, detection, vehicle_state, environment
    data = Column(JSON, nullable=False)  # Actual sensor/state data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
