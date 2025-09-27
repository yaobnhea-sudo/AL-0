from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from app.api import models, inference, simulations, telemetry, datasets, optimization, monitoring
from app.core.config import settings
from app.core.database import init_db
from app.services.model_service import ModelService
from app.services.telemetry_service import TelemetryService
from app.services.monitoring_service import monitoring_service
from app.services.model_optimization import ModelOptimizer
from app.services.security_service import SecurityService
from app.core.security import setup_security_middleware
import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting AL-0 API...")
    
    # Initialize database
    await init_db()
    
    # Initialize Redis
    redis_client = redis.Redis.from_url(settings.REDIS_URL)
    app.state.redis_client = redis_client
    
    # Initialize security service
    security_service = SecurityService(settings.SECRET_KEY, redis_client)
    app.state.security_service = security_service
    
    # Initialize model service
    model_service = ModelService()
    await model_service.initialize()
    app.state.model_service = model_service
    
    # Initialize model optimizer
    model_optimizer = ModelOptimizer()
    app.state.model_optimizer = model_optimizer
    
    # Initialize telemetry service
    telemetry_service = TelemetryService()
    app.state.telemetry_service = telemetry_service
    
    # Start monitoring service
    await monitoring_service.start_monitoring(port=8001)
    app.state.monitoring_service = monitoring_service
    
    # Setup security middleware
    setup_security_middleware(app, redis_client)
    
    print("API startup complete!")
    
    yield
    
    # Shutdown
    print("Shutting down AL-0 API...")
    await monitoring_service.stop_monitoring()


# Create FastAPI app
app = FastAPI(
    title="AL-0 API",
    description="A comprehensive ML systems platform featuring self-driving simulators, object detection, segmentation, and predictive models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(models.router, prefix="/api", tags=["models"])
app.include_router(inference.router, prefix="/api", tags=["inference"])
app.include_router(simulations.router, prefix="/api", tags=["simulations"])
app.include_router(telemetry.router, prefix="/api", tags=["telemetry"])
app.include_router(datasets.router, prefix="/api", tags=["datasets"])
app.include_router(optimization.router, prefix="/api", tags=["optimization"])
app.include_router(monitoring.router, prefix="/api", tags=["monitoring"])


@app.get("/")
async def root():
    return {
        "message": "AL-0 API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "message": "An error occurred while processing your request"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
