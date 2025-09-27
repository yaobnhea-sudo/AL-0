import time
import psutil
import GPUtil
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
import json

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Prometheus metrics for monitoring"""
    
    def __init__(self):
        # API metrics
        self.api_requests_total = Counter(
            'api_requests_total',
            'Total number of API requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.api_request_duration = Histogram(
            'api_request_duration_seconds',
            'API request duration in seconds',
            ['method', 'endpoint']
        )
        
        # Model inference metrics
        self.model_inference_total = Counter(
            'model_inference_total',
            'Total number of model inferences',
            ['model_id', 'model_type', 'status']
        )
        
        self.model_inference_duration = Histogram(
            'model_inference_duration_seconds',
            'Model inference duration in seconds',
            ['model_id', 'model_type']
        )
        
        self.model_inference_accuracy = Gauge(
            'model_inference_accuracy',
            'Model inference accuracy',
            ['model_id', 'model_type']
        )
        
        # System metrics
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'System CPU usage percentage'
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_percent',
            'System memory usage percentage'
        )
        
        self.system_gpu_usage = Gauge(
            'system_gpu_usage_percent',
            'System GPU usage percentage',
            ['gpu_id']
        )
        
        self.system_gpu_memory_usage = Gauge(
            'system_gpu_memory_usage_percent',
            'System GPU memory usage percentage',
            ['gpu_id']
        )
        
        # WebSocket metrics
        self.websocket_connections = Gauge(
            'websocket_connections_total',
            'Total number of WebSocket connections'
        )
        
        self.websocket_messages_sent = Counter(
            'websocket_messages_sent_total',
            'Total number of WebSocket messages sent',
            ['connection_type']
        )
        
        # Simulation metrics
        self.simulation_runs_total = Counter(
            'simulation_runs_total',
            'Total number of simulation runs',
            ['status']
        )
        
        self.simulation_duration = Histogram(
            'simulation_duration_seconds',
            'Simulation duration in seconds',
            ['simulation_id']
        )
        
        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total number of errors',
            ['error_type', 'component']
        )
        
        # Performance metrics
        self.fps_gauge = Gauge(
            'system_fps',
            'System FPS'
        )
        
        self.latency_gauge = Gauge(
            'system_latency_ms',
            'System latency in milliseconds'
        )


class MonitoringService:
    """Comprehensive monitoring service"""
    
    def __init__(self):
        self.metrics = PrometheusMetrics()
        self.is_monitoring = False
        self.monitoring_task = None
        self.start_time = datetime.now()
        self.performance_history = []
        self.max_history_size = 1000
        
    async def start_monitoring(self, port: int = 8001):
        """Start monitoring service"""
        try:
            # Start Prometheus metrics server
            start_http_server(port)
            logger.info(f"Prometheus metrics server started on port {port}")
            
            # Start background monitoring
            self.is_monitoring = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("Monitoring service started")
            
        except Exception as e:
            logger.error(f"Error starting monitoring service: {e}")
            raise
    
    async def stop_monitoring(self):
        """Stop monitoring service"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Monitoring service stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect performance metrics
                await self._collect_performance_metrics()
                
                # Update Prometheus metrics
                await self._update_prometheus_metrics()
                
                # Store metrics in history
                await self._store_metrics_history()
                
                await asyncio.sleep(1)  # Collect every second
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _collect_system_metrics(self):
        """Collect system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.system_memory_usage.set(memory.percent)
            
            # GPU usage (if available)
            try:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    self.metrics.system_gpu_usage.labels(gpu_id=i).set(gpu.load * 100)
                    self.metrics.system_gpu_memory_usage.labels(gpu_id=i).set(
                        (gpu.memoryUsed / gpu.memoryTotal) * 100
                    )
            except Exception:
                # GPU not available or error
                pass
                
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _collect_performance_metrics(self):
        """Collect performance metrics"""
        try:
            # Calculate FPS (simplified)
            current_time = time.time()
            if hasattr(self, '_last_fps_time'):
                time_diff = current_time - self._last_fps_time
                if time_diff > 0:
                    fps = 1.0 / time_diff
                    self.metrics.fps_gauge.set(fps)
            self._last_fps_time = current_time
            
            # Calculate latency (simplified)
            latency = self._calculate_average_latency()
            self.metrics.latency_gauge.set(latency)
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
    
    def _calculate_average_latency(self) -> float:
        """Calculate average latency from recent history"""
        if not self.performance_history:
            return 0.0
        
        recent_history = self.performance_history[-10:]  # Last 10 measurements
        latencies = [entry.get('latency', 0) for entry in recent_history]
        return sum(latencies) / len(latencies) if latencies else 0.0
    
    async def _update_prometheus_metrics(self):
        """Update Prometheus metrics"""
        try:
            # Update WebSocket connections
            # This would be updated by the WebSocket manager
            pass
            
        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")
    
    async def _store_metrics_history(self):
        """Store metrics in history for analysis"""
        try:
            current_metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'latency': self._calculate_average_latency(),
                'fps': self._get_current_fps()
            }
            
            # Add GPU metrics if available
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    current_metrics['gpu_usage'] = gpus[0].load * 100
                    current_metrics['gpu_memory_usage'] = (gpus[0].memoryUsed / gpus[0].memoryTotal) * 100
            except Exception:
                pass
            
            self.performance_history.append(current_metrics)
            
            # Keep only recent history
            if len(self.performance_history) > self.max_history_size:
                self.performance_history = self.performance_history[-self.max_history_size:]
                
        except Exception as e:
            logger.error(f"Error storing metrics history: {e}")
    
    def _get_current_fps(self) -> float:
        """Get current FPS"""
        if hasattr(self, '_last_fps_time'):
            current_time = time.time()
            time_diff = current_time - self._last_fps_time
            if time_diff > 0:
                return 1.0 / time_diff
        return 0.0
    
    def record_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics"""
        self.metrics.api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.metrics.api_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_model_inference(self, model_id: str, model_type: str, duration: float, 
                             accuracy: float = None, status: str = 'success'):
        """Record model inference metrics"""
        self.metrics.model_inference_total.labels(
            model_id=model_id,
            model_type=model_type,
            status=status
        ).inc()
        
        self.metrics.model_inference_duration.labels(
            model_id=model_id,
            model_type=model_type
        ).observe(duration)
        
        if accuracy is not None:
            self.metrics.model_inference_accuracy.labels(
                model_id=model_id,
                model_type=model_type
            ).set(accuracy)
    
    def record_websocket_message(self, connection_type: str):
        """Record WebSocket message sent"""
        self.metrics.websocket_messages_sent.labels(
            connection_type=connection_type
        ).inc()
    
    def record_simulation_run(self, simulation_id: str, status: str, duration: float = None):
        """Record simulation run metrics"""
        self.metrics.simulation_runs_total.labels(status=status).inc()
        
        if duration is not None:
            self.metrics.simulation_duration.labels(
                simulation_id=simulation_id
            ).observe(duration)
    
    def record_error(self, error_type: str, component: str):
        """Record error metrics"""
        self.metrics.errors_total.labels(
            error_type=error_type,
            component=component
        ).inc()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        try:
            # Basic health checks
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            # Determine health status
            health_status = "healthy"
            if cpu_usage > 90 or memory_usage > 90 or disk_usage > 90:
                health_status = "critical"
            elif cpu_usage > 80 or memory_usage > 80 or disk_usage > 80:
                health_status = "warning"
            
            # Get uptime
            uptime = datetime.now() - self.start_time
            
            return {
                'status': health_status,
                'uptime_seconds': uptime.total_seconds(),
                'cpu_usage_percent': cpu_usage,
                'memory_usage_percent': memory_usage,
                'disk_usage_percent': disk_usage,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter recent history
            recent_history = [
                entry for entry in self.performance_history
                if datetime.fromisoformat(entry['timestamp']) > cutoff_time
            ]
            
            if not recent_history:
                return {'error': 'No data available for the specified time period'}
            
            # Calculate statistics
            cpu_values = [entry.get('cpu_usage', 0) for entry in recent_history]
            memory_values = [entry.get('memory_usage', 0) for entry in recent_history]
            latency_values = [entry.get('latency', 0) for entry in recent_history]
            fps_values = [entry.get('fps', 0) for entry in recent_history]
            
            return {
                'time_period_hours': hours,
                'data_points': len(recent_history),
                'cpu_usage': {
                    'average': sum(cpu_values) / len(cpu_values),
                    'min': min(cpu_values),
                    'max': max(cpu_values),
                    'current': cpu_values[-1] if cpu_values else 0
                },
                'memory_usage': {
                    'average': sum(memory_values) / len(memory_values),
                    'min': min(memory_values),
                    'max': max(memory_values),
                    'current': memory_values[-1] if memory_values else 0
                },
                'latency': {
                    'average': sum(latency_values) / len(latency_values),
                    'min': min(latency_values),
                    'max': max(latency_values),
                    'current': latency_values[-1] if latency_values else 0
                },
                'fps': {
                    'average': sum(fps_values) / len(fps_values),
                    'min': min(fps_values),
                    'max': max(fps_values),
                    'current': fps_values[-1] if fps_values else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}
    
    def get_metrics_export(self) -> Dict[str, Any]:
        """Export all metrics for external monitoring systems"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'system_health': self.get_system_health(),
                'performance_summary': self.get_performance_summary(hours=1),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                'monitoring_active': self.is_monitoring
            }
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return {'error': str(e)}


# Global monitoring service instance
monitoring_service = MonitoringService()
