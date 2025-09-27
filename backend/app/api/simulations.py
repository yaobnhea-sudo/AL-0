from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
import json
import asyncio
from datetime import datetime

from app.core.database import get_db
from app.services.simulation_service import SimulationService
from app.schemas.simulation import (
    SimulationRunResponse,
    SimulationRunListResponse,
    SimulationConfigRequest,
    SimulationConfigResponse
)

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, run_id: str):
        await websocket.accept()
        self.active_connections[run_id] = websocket

    def disconnect(self, run_id: str):
        if run_id in self.active_connections:
            del self.active_connections[run_id]

    async def send_personal_message(self, message: str, run_id: str):
        if run_id in self.active_connections:
            try:
                await self.active_connections[run_id].send_text(message)
            except:
                self.disconnect(run_id)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()


@router.get("/simulations", response_model=SimulationRunListResponse)
async def get_simulations(
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get list of simulation runs"""
    try:
        simulation_service = SimulationService()
        simulations = await simulation_service.get_simulations(
            db=db,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return SimulationRunListResponse(
            success=True,
            data=simulations,
            total=len(simulations)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulations", response_model=SimulationRunResponse)
async def create_simulation(
    config: SimulationConfigRequest,
    db: Session = Depends(get_db)
):
    """Create a new simulation run"""
    try:
        simulation_service = SimulationService()
        simulation = await simulation_service.create_simulation(
            db=db,
            config=config
        )
        
        return SimulationRunResponse(
            success=True,
            data=simulation,
            message="Simulation created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulations/{run_id}", response_model=SimulationRunResponse)
async def get_simulation(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Get details of a specific simulation run"""
    try:
        simulation_service = SimulationService()
        simulation = await simulation_service.get_simulation(
            db=db,
            run_id=run_id
        )
        
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulation not found")
        
        return SimulationRunResponse(
            success=True,
            data=simulation
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulations/{run_id}/start")
async def start_simulation(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Start a simulation run"""
    try:
        simulation_service = SimulationService()
        success = await simulation_service.start_simulation(
            db=db,
            run_id=run_id
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to start simulation")
        
        return {
            "success": True,
            "message": f"Simulation {run_id} started",
            "run_id": run_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulations/{run_id}/pause")
async def pause_simulation(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Pause a simulation run"""
    try:
        simulation_service = SimulationService()
        success = await simulation_service.pause_simulation(
            db=db,
            run_id=run_id
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to pause simulation")
        
        return {
            "success": True,
            "message": f"Simulation {run_id} paused",
            "run_id": run_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulations/{run_id}/stop")
async def stop_simulation(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Stop a simulation run"""
    try:
        simulation_service = SimulationService()
        success = await simulation_service.stop_simulation(
            db=db,
            run_id=run_id
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to stop simulation")
        
        return {
            "success": True,
            "message": f"Simulation {run_id} stopped",
            "run_id": run_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/simulations/{run_id}")
async def delete_simulation(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Delete a simulation run"""
    try:
        simulation_service = SimulationService()
        success = await simulation_service.delete_simulation(
            db=db,
            run_id=run_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Simulation not found")
        
        return {
            "success": True,
            "message": f"Simulation {run_id} deleted",
            "run_id": run_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/sim/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    """WebSocket endpoint for real-time simulation data"""
    await manager.connect(websocket, run_id)
    
    try:
        # Send initial connection message
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "run_id": run_id,
                "message": "Connected to simulation stream",
                "timestamp": datetime.now().isoformat()
            }),
            run_id
        )
        
        # Start simulation data stream
        simulation_service = SimulationService()
        await simulation_service.stream_simulation_data(run_id, manager)
        
    except WebSocketDisconnect:
        manager.disconnect(run_id)
    except Exception as e:
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "run_id": run_id,
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }),
            run_id
        )
        manager.disconnect(run_id)


@router.get("/simulations/{run_id}/data")
async def get_simulation_data(
    run_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get historical simulation data"""
    try:
        simulation_service = SimulationService()
        data = await simulation_service.get_simulation_data(
            db=db,
            run_id=run_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        return {
            "success": True,
            "data": data,
            "run_id": run_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
