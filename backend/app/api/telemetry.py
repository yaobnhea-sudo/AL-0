from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import json
import asyncio
from datetime import datetime, timedelta

from app.core.database import get_db
from app.services.telemetry_service import TelemetryService
from app.schemas.telemetry import (
    TelemetryDataResponse,
    TelemetryHistoryResponse,
    TelemetryMetricsResponse
)

router = APIRouter()

# WebSocket connection manager for telemetry
class TelemetryConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

telemetry_manager = TelemetryConnectionManager()


@router.get("/telemetry", response_model=TelemetryDataResponse)
async def get_current_telemetry(
    db: Session = Depends(get_db)
):
    """Get current system telemetry data"""
    try:
        telemetry_service = TelemetryService()
        data = await telemetry_service.get_current_telemetry(db=db)
        
        return TelemetryDataResponse(
            success=True,
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/telemetry/history", response_model=TelemetryHistoryResponse)
async def get_telemetry_history(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get historical telemetry data"""
    try:
        telemetry_service = TelemetryService()
        
        # Parse time parameters
        start_dt = None
        end_dt = None
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # Default to last hour if no time range specified
        if not start_dt and not end_dt:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(hours=1)
        
        data = await telemetry_service.get_telemetry_history(
            db=db,
            start_time=start_dt,
            end_time=end_dt,
            limit=limit
        )
        
        return TelemetryHistoryResponse(
            success=True,
            data=data,
            start_time=start_dt.isoformat() if start_dt else None,
            end_time=end_dt.isoformat() if end_dt else None,
            total=len(data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/telemetry/metrics", response_model=TelemetryMetricsResponse)
async def get_telemetry_metrics(
    metric_type: Optional[str] = None,
    time_range: str = "1h",
    db: Session = Depends(get_db)
):
    """Get aggregated telemetry metrics"""
    try:
        telemetry_service = TelemetryService()
        
        # Parse time range
        time_ranges = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        
        if time_range not in time_ranges:
            raise HTTPException(status_code=400, detail="Invalid time range")
        
        end_time = datetime.now()
        start_time = end_time - time_ranges[time_range]
        
        metrics = await telemetry_service.get_telemetry_metrics(
            db=db,
            start_time=start_time,
            end_time=end_time,
            metric_type=metric_type
        )
        
        return TelemetryMetricsResponse(
            success=True,
            data=metrics,
            time_range=time_range,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry data"""
    await telemetry_manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "Connected to telemetry stream",
            "timestamp": datetime.now().isoformat()
        }))
        
        # Start telemetry data stream
        telemetry_service = TelemetryService()
        await telemetry_service.stream_telemetry_data(telemetry_manager)
        
    except WebSocketDisconnect:
        telemetry_manager.disconnect(websocket)
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }))
        telemetry_manager.disconnect(websocket)


@router.post("/telemetry/collect")
async def collect_telemetry(
    db: Session = Depends(get_db)
):
    """Manually trigger telemetry data collection"""
    try:
        telemetry_service = TelemetryService()
        await telemetry_service.collect_telemetry_data(db=db)
        
        return {
            "success": True,
            "message": "Telemetry data collected successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/telemetry/health")
async def get_telemetry_health():
    """Get telemetry system health status"""
    try:
        return {
            "success": True,
            "status": "healthy",
            "active_connections": len(telemetry_manager.active_connections),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
