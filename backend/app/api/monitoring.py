from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.monitoring_service import monitoring_service

router = APIRouter()


@router.get("/health")
async def get_system_health():
    """Get comprehensive system health status"""
    try:
        health = monitoring_service.get_system_health()
        return {
            "success": True,
            "data": health
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics_export():
    """Export all metrics for external monitoring systems"""
    try:
        metrics = monitoring_service.get_metrics_export()
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance_summary(hours: int = 1):
    """Get performance summary for the last N hours"""
    try:
        summary = monitoring_service.get_performance_summary(hours)
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prometheus")
async def get_prometheus_metrics():
    """Get Prometheus-formatted metrics"""
    try:
        # In a real implementation, this would return Prometheus format
        # For now, return a simple status
        return {
            "success": True,
            "message": "Prometheus metrics available at /metrics",
            "endpoint": "http://localhost:8001/metrics"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alert")
async def create_alert(
    alert_type: str,
    severity: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """Create a monitoring alert"""
    try:
        # Log the alert
        monitoring_service.metrics.errors_total.labels(
            error_type=alert_type,
            component="monitoring"
        ).inc()
        
        return {
            "success": True,
            "message": "Alert created successfully",
            "alert": {
                "type": alert_type,
                "severity": severity,
                "message": message,
                "metadata": metadata or {}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts():
    """Get recent alerts and notifications"""
    try:
        # In a real implementation, this would query a database
        # For now, return mock data
        alerts = [
            {
                "id": "alert_1",
                "type": "high_cpu_usage",
                "severity": "warning",
                "message": "CPU usage above 80%",
                "timestamp": "2024-01-01T12:00:00Z",
                "resolved": False
            },
            {
                "id": "alert_2",
                "type": "model_inference_error",
                "severity": "error",
                "message": "Model inference failed",
                "timestamp": "2024-01-01T11:30:00Z",
                "resolved": True
            }
        ]
        
        return {
            "success": True,
            "data": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
