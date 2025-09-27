from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class MVPSettings(BaseSettings):
    """Simplified settings for MVP version"""
    
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "AL-0 MVP"
    VERSION: str = "1.0.0-mvp"
    
    # CORS Settings (simplified)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Database Settings (SQLite for simplicity)
    DATABASE_URL: str = "sqlite:///./al_0.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Model Settings (simplified)
    MODEL_CACHE_DIR: str = "./models"
    MAX_MODEL_SIZE_MB: int = 100  # Reduced for MVP
    SUPPORTED_MODEL_FORMATS: List[str] = ["onnx"]  # Only ONNX for MVP
    
    # Inference Settings (reduced for MVP)
    MAX_IMAGE_SIZE_MB: int = 5  # Reduced
    MAX_VIDEO_SIZE_MB: int = 50  # Reduced
    MAX_BATCH_SIZE: int = 1  # Reduced
    INFERENCE_TIMEOUT: int = 10  # Reduced
    
    # Security Settings (simplified)
    SECRET_KEY: str = "mvp-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Longer for MVP
    ALGORITHM: str = "HS256"
    
    # Monitoring Settings (minimal)
    ENABLE_TELEMETRY: bool = True
    TELEMETRY_INTERVAL: int = 30  # Less frequent
    METRICS_RETENTION_DAYS: int = 7  # Shorter retention
    
    # GPU Settings (disabled for MVP)
    CUDA_VISIBLE_DEVICES: Optional[str] = None
    ENABLE_GPU: bool = False  # Disabled for MVP
    
    # File Upload Settings
    UPLOAD_DIR: str = "./uploads"
    TEMP_DIR: str = "./temp"
    
    # Logging Settings (simplified)
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
    
    # MVP-specific settings
    ENABLE_COMPLEX_FEATURES: bool = False
    ENABLE_3D_SIMULATION: bool = True  # Keep 3D as it's core
    ENABLE_ADVANCED_MONITORING: bool = False
    ENABLE_ML_OPTIMIZATION: bool = False
    
    class Config:
        env_file = ".env.mvp"
        case_sensitive = True


# Create MVP settings instance
mvp_settings = MVPSettings()

# Ensure directories exist
os.makedirs(mvp_settings.MODEL_CACHE_DIR, exist_ok=True)
os.makedirs(mvp_settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(mvp_settings.TEMP_DIR, exist_ok=True)
