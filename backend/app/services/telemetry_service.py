import asyncio
import json
import random
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.telemetry import TelemetryData, TelemetryMetrics
import logging

logger = logging.getLogger(__name__)


class TelemetryService:
    def __init__(self):
        self.is_collecting = False
        self.collection_task = None
    
    async def get_current_telemetry(self, db: Session) -> TelemetryData:
        """Get current system telemetry data"""
        # For demo purposes, generate mock telemetry data
        # In a real implementation, this would collect actual system metrics
        
        current_time = datetime.now()
        
        # Generate realistic telemetry data
        fps = random.uniform(25, 60)
        latency = random.uniform(10, 50)
        cpu_usage = random.uniform(20, 80)
        gpu_usage = random.uniform(10, 70)
        memory_usage = random.uniform(30, 90)
        
        model_inference = {
            "detection": random.uniform(5, 20),
            "segmentation": random.uniform(15, 45),
            "lidar": random.uniform(8, 25)
        }
        
        telemetry = TelemetryData(
            timestamp=current_time,
            fps=fps,
            latency=latency,
            cpu_usage=cpu_usage,
            gpu_usage=gpu_usage,
            memory_usage=memory_usage,
            model_inference=model_inference
        )
        
        return telemetry
    
    async def get_telemetry_history(
        self,
        db: Session,
        start_time: datetime,
        end_time: datetime,
        limit: int = 100
    ) -> List[TelemetryData]:
        """Get historical telemetry data"""
        # For demo purposes, generate mock historical data
        # In a real implementation, this would query the database
        
        data_points = []
        current_time = start_time
        
        while current_time <= end_time and len(data_points) < limit:
            # Generate telemetry data for this timestamp
            fps = random.uniform(25, 60)
            latency = random.uniform(10, 50)
            cpu_usage = random.uniform(20, 80)
            gpu_usage = random.uniform(10, 70)
            memory_usage = random.uniform(30, 90)
            
            model_inference = {
                "detection": random.uniform(5, 20),
                "segmentation": random.uniform(15, 45),
                "lidar": random.uniform(8, 25)
            }
            
            telemetry = TelemetryData(
                timestamp=current_time,
                fps=fps,
                latency=latency,
                cpu_usage=cpu_usage,
                gpu_usage=gpu_usage,
                memory_usage=memory_usage,
                model_inference=model_inference
            )
            
            data_points.append(telemetry)
            current_time += timedelta(seconds=1)
        
        return data_points
    
    async def get_telemetry_metrics(
        self,
        db: Session,
        start_time: datetime,
        end_time: datetime,
        metric_type: Optional[str] = None
    ) -> List[TelemetryMetrics]:
        """Get aggregated telemetry metrics"""
        # For demo purposes, generate mock metrics
        # In a real implementation, this would calculate actual metrics from historical data
        
        metrics = []
        metric_types = ["fps", "latency", "cpu_usage", "gpu_usage", "memory_usage"]
        
        if metric_type:
            metric_types = [metric_type]
        
        for mtype in metric_types:
            # Generate realistic metrics
            if mtype == "fps":
                values = [random.uniform(25, 60) for _ in range(100)]
            elif mtype == "latency":
                values = [random.uniform(10, 50) for _ in range(100)]
            elif mtype == "cpu_usage":
                values = [random.uniform(20, 80) for _ in range(100)]
            elif mtype == "gpu_usage":
                values = [random.uniform(10, 70) for _ in range(100)]
            elif mtype == "memory_usage":
                values = [random.uniform(30, 90) for _ in range(100)]
            else:
                values = [random.uniform(0, 100) for _ in range(100)]
            
            # Calculate statistics
            values.sort()
            count = len(values)
            average = sum(values) / count
            min_value = values[0]
            max_value = values[-1]
            median = values[count // 2]
            p95 = values[int(count * 0.95)]
            p99 = values[int(count * 0.99)]
            
            metric = TelemetryMetrics(
                metric_type=mtype,
                time_range="1h",
                average=average,
                min_value=min_value,
                max_value=max_value,
                median=median,
                p95=p95,
                p99=p99,
                count=count,
                start_time=start_time,
                end_time=end_time
            )
            
            metrics.append(metric)
        
        return metrics
    
    async def collect_telemetry_data(self, db: Session):
        """Collect and store telemetry data"""
        try:
            # Get current telemetry
            telemetry = await self.get_current_telemetry(db)
            
            # Store in database
            db_telemetry = TelemetryData(
                timestamp=telemetry.timestamp,
                fps=telemetry.fps,
                latency=telemetry.latency,
                cpu_usage=telemetry.cpu_usage,
                gpu_usage=telemetry.gpu_usage,
                memory_usage=telemetry.memory_usage,
                model_inference=telemetry.model_inference
            )
            
            db.add(db_telemetry)
            db.commit()
            
            logger.info("Telemetry data collected and stored")
            
        except Exception as e:
            logger.error(f"Error collecting telemetry data: {e}")
    
    async def start_telemetry_collection(self, db: Session, interval: int = 1):
        """Start continuous telemetry data collection"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        
        async def collect_loop():
            while self.is_collecting:
                try:
                    await self.collect_telemetry_data(db)
                    await asyncio.sleep(interval)
                except Exception as e:
                    logger.error(f"Error in telemetry collection loop: {e}")
                    await asyncio.sleep(interval)
        
        self.collection_task = asyncio.create_task(collect_loop())
        logger.info("Telemetry collection started")
    
    async def stop_telemetry_collection(self):
        """Stop continuous telemetry data collection"""
        if not self.is_collecting:
            return
        
        self.is_collecting = False
        
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Telemetry collection stopped")
    
    async def stream_telemetry_data(self, manager):
        """Stream telemetry data via WebSocket"""
        try:
            while True:
                # Generate current telemetry data
                telemetry = await self.get_current_telemetry(None)
                
                # Send data via WebSocket
                await manager.broadcast(json.dumps({
                    "type": "telemetry",
                    "data": {
                        "timestamp": telemetry.timestamp.isoformat(),
                        "fps": telemetry.fps,
                        "latency": telemetry.latency,
                        "cpu_usage": telemetry.cpu_usage,
                        "gpu_usage": telemetry.gpu_usage,
                        "memory_usage": telemetry.memory_usage,
                        "model_inference": telemetry.model_inference
                    }
                }))
                
                await asyncio.sleep(1)  # Send every second
                
        except Exception as e:
            logger.error(f"Error streaming telemetry data: {e}")
    
    async def cleanup_old_data(self, db: Session, days: int = 30):
        """Clean up old telemetry data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Delete old telemetry data
            deleted_count = db.query(TelemetryData).filter(
                TelemetryData.timestamp < cutoff_date
            ).delete()
            
            db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old telemetry records")
            
        except Exception as e:
            logger.error(f"Error cleaning up old telemetry data: {e}")
