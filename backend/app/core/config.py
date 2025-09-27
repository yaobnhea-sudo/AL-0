from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "AL-0 API"
    VERSION: str = "1.0.0"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./al_0.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Model Settings
    MODEL_CACHE_DIR: str = "./models"
    MAX_MODEL_SIZE_MB: int = 500
    SUPPORTED_MODEL_FORMATS: List[str] = ["onnx", "pt", "pth"]
    
    # Inference Settings
    MAX_IMAGE_SIZE_MB: int = 10
    MAX_VIDEO_SIZE_MB: int = 100
    MAX_BATCH_SIZE: int = 8
    INFERENCE_TIMEOUT: int = 30
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Monitoring Settings
    ENABLE_TELEMETRY: bool = True
    TELEMETRY_INTERVAL: int = 1  # seconds
    METRICS_RETENTION_DAYS: int = 30
    
    # GPU Settings
    CUDA_VISIBLE_DEVICES: Optional[str] = None
    ENABLE_GPU: bool = True
    
    # File Upload Settings
    UPLOAD_DIR: str = "./uploads"
    TEMP_DIR: str = "./temp"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
