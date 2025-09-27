import asyncio
import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.simulation import SimulationRun, SimulationData
from app.schemas.simulation import SimulationConfigRequest, SimulationConfig
import logging

logger = logging.getLogger(__name__)


class SimulationService:
    def __init__(self):
        self.active_simulations: Dict[str, Dict[str, Any]] = {}
    
    async def get_simulations(
        self,
        db: Session,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[SimulationRun]:
        """Get list of simulation runs"""
        query = db.query(SimulationRun)
        
        if status:
            query = query.filter(SimulationRun.status == status)
        
        return query.offset(offset).limit(limit).all()
    
    async def get_simulation(self, db: Session, run_id: str) -> Optional[SimulationRun]:
        """Get a specific simulation run"""
        return db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    
    async def create_simulation(
        self,
        db: Session,
        config: SimulationConfigRequest
    ) -> SimulationRun:
        """Create a new simulation run"""
        simulation = SimulationRun(
            id=str(uuid.uuid4()),
            name=config.name,
            status="pending",
            config=config.config.dict()
        )
        
        db.add(simulation)
        db.commit()
        db.refresh(simulation)
        
        return simulation
    
    async def start_simulation(self, db: Session, run_id: str) -> bool:
        """Start a simulation run"""
        simulation = await self.get_simulation(db, run_id)
        if not simulation:
            return False
        
        if simulation.status != "pending":
            return False
        
        # Update status
        simulation.status = "running"
        simulation.start_time = datetime.now()
        db.commit()
        
        # Start simulation in background
        asyncio.create_task(self._run_simulation(run_id, simulation.config))
        
        return True
    
    async def pause_simulation(self, db: Session, run_id: str) -> bool:
        """Pause a simulation run"""
        simulation = await self.get_simulation(db, run_id)
        if not simulation:
            return False
        
        if simulation.status != "running":
            return False
        
        simulation.status = "paused"
        db.commit()
        
        return True
    
    async def stop_simulation(self, db: Session, run_id: str) -> bool:
        """Stop a simulation run"""
        simulation = await self.get_simulation(db, run_id)
        if not simulation:
            return False
        
        if simulation.status not in ["running", "paused"]:
            return False
        
        simulation.status = "stopped"
        simulation.end_time = datetime.now()
        if simulation.start_time:
            simulation.duration = int((simulation.end_time - simulation.start_time).total_seconds())
        db.commit()
        
        return True
    
    async def delete_simulation(self, db: Session, run_id: str) -> bool:
        """Delete a simulation run"""
        simulation = await self.get_simulation(db, run_id)
        if not simulation:
            return False
        
        # Delete associated data
        db.query(SimulationData).filter(SimulationData.run_id == run_id).delete()
        db.delete(simulation)
        db.commit()
        
        return True
    
    async def get_simulation_data(
        self,
        db: Session,
        run_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SimulationData]:
        """Get simulation data for a specific run"""
        query = db.query(SimulationData).filter(SimulationData.run_id == run_id)
        
        if start_time:
            query = query.filter(SimulationData.timestamp >= start_time)
        if end_time:
            query = query.filter(SimulationData.timestamp <= end_time)
        
        return query.order_by(SimulationData.timestamp.desc()).limit(limit).all()
    
    async def stream_simulation_data(self, run_id: str, manager):
        """Stream simulation data via WebSocket"""
        try:
            frame_count = 0
            while True:
                # Check if simulation is still active
                if run_id not in self.active_simulations:
                    break
                
                # Generate simulation data
                data = await self._generate_simulation_data(run_id, frame_count)
                
                # Send data via WebSocket
                await manager.send_personal_message(
                    json.dumps(data),
                    run_id
                )
                
                frame_count += 1
                await asyncio.sleep(0.1)  # 10 FPS
                
        except Exception as e:
            logger.error(f"Error streaming simulation data: {e}")
    
    async def _run_simulation(self, run_id: str, config: Dict[str, Any]):
        """Run simulation in background"""
        try:
            self.active_simulations[run_id] = {
                "config": config,
                "start_time": datetime.now(),
                "status": "running"
            }
            
            # Simulate simulation duration
            duration = config.get("duration", 60)  # Default 60 seconds
            await asyncio.sleep(duration)
            
            # Mark simulation as completed
            if run_id in self.active_simulations:
                self.active_simulations[run_id]["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Error running simulation {run_id}: {e}")
            if run_id in self.active_simulations:
                self.active_simulations[run_id]["status"] = "failed"
    
    async def _generate_simulation_data(self, run_id: str, frame_count: int) -> Dict[str, Any]:
        """Generate simulation data for a frame"""
        # Simulate camera data
        camera_data = {
            "frame_number": frame_count,
            "timestamp": datetime.now().isoformat(),
            "resolution": {"width": 1920, "height": 1080},
            "fps": 30
        }
        
        # Simulate LIDAR data
        lidar_data = {
            "frame_number": frame_count,
            "timestamp": datetime.now().isoformat(),
            "point_count": 1000,
            "range": 100.0
        }
        
        # Simulate detections
        detections = []
        for i in range(5):  # Simulate 5 detections per frame
            detection = {
                "id": f"det_{frame_count}_{i}",
                "class": "car",
                "confidence": 0.85 + (i * 0.02),
                "bbox": {
                    "x": 100 + i * 200,
                    "y": 200 + i * 50,
                    "width": 150,
                    "height": 100
                }
            }
            detections.append(detection)
        
        # Simulate vehicle state
        vehicle_state = {
            "position": {"x": frame_count * 0.1, "y": 0, "z": 0},
            "velocity": {"x": 10.0, "y": 0, "z": 0},
            "acceleration": {"x": 0, "y": 0, "z": 0},
            "heading": frame_count * 0.01
        }
        
        return {
            "type": "simulation_data",
            "run_id": run_id,
            "frame_number": frame_count,
            "timestamp": datetime.now().isoformat(),
            "camera_data": camera_data,
            "lidar_data": lidar_data,
            "detections": detections,
            "vehicle_state": vehicle_state
        }
