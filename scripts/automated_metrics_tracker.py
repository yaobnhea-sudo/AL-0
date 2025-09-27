#!/usr/bin/env python3
"""
AL-0 Automated Metrics Tracker
Measures startup time and memory usage during builds with hardware awareness
"""

import os
import time
import psutil
import subprocess
import json
import platform
import GPUtil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading
import queue

class AutomatedMetricsTracker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.metrics_dir = self.project_root / 'monitoring' / 'metrics'
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.hardware_info = self.detect_hardware()
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'hardware': self.hardware_info,
            'startup_metrics': {},
            'memory_metrics': {},
            'ml_model_metrics': {},
            'build_metrics': {}
        }
        
        self.monitoring_active = False
        self.monitoring_thread = None
        self.metrics_queue = queue.Queue()
    
    def detect_hardware(self) -> Dict[str, Any]:
        """Detect hardware configuration and capabilities"""
        hardware = {
            'platform': platform.platform(),
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'gpu_available': False,
            'gpu_info': {},
            'ml_acceleration': 'cpu'  # Default to CPU
        }
        
        # Detect GPU availability
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                hardware['gpu_available'] = True
                hardware['gpu_count'] = len(gpus)
                hardware['gpu_info'] = {
                    'name': gpus[0].name,
                    'memory_total': gpus[0].memoryTotal,
                    'memory_used': gpus[0].memoryUsed,
                    'memory_free': gpus[0].memoryFree,
                    'temperature': gpus[0].temperature,
                    'load': gpus[0].load
                }
                hardware['ml_acceleration'] = 'gpu'
        except:
            # GPU detection failed, continue with CPU
            pass
        
        # Detect ML frameworks
        hardware['ml_frameworks'] = self.detect_ml_frameworks()
        
        return hardware
    
    def detect_ml_frameworks(self) -> List[str]:
        """Detect available ML frameworks"""
        frameworks = []
        
        try:
            import torch
            frameworks.append('pytorch')
            if torch.cuda.is_available():
                frameworks.append('pytorch_cuda')
        except ImportError:
            pass
        
        try:
            import tensorflow as tf
            frameworks.append('tensorflow')
            if tf.config.list_physical_devices('GPU'):
                frameworks.append('tensorflow_gpu')
        except ImportError:
            pass
        
        try:
            import onnxruntime
            frameworks.append('onnx')
            if onnxruntime.get_device() == 'GPU':
                frameworks.append('onnx_gpu')
        except ImportError:
            pass
        
        return frameworks
    
    def start_monitoring(self):
        """Start background monitoring of system metrics"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_system)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        print("🔍 Started automated metrics monitoring")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("⏹️  Stopped automated metrics monitoring")
    
    def _monitor_system(self):
        """Background thread for monitoring system metrics"""
        while self.monitoring_active:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_freq = psutil.cpu_freq()
                
                # Memory metrics
                memory = psutil.virtual_memory()
                
                # GPU metrics (if available)
                gpu_metrics = {}
                if self.hardware_info['gpu_available']:
                    try:
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            gpu = gpus[0]
                            gpu_metrics = {
                                'memory_used': gpu.memoryUsed,
                                'memory_free': gpu.memoryFree,
                                'temperature': gpu.temperature,
                                'load': gpu.load
                            }
                    except:
                        pass
                
                # Store metrics
                metrics_data = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': cpu_percent,
                    'cpu_freq': cpu_freq._asdict() if cpu_freq else None,
                    'memory_percent': memory.percent,
                    'memory_used': memory.used,
                    'memory_available': memory.available,
                    'gpu_metrics': gpu_metrics
                }
                
                self.metrics_queue.put(metrics_data)
                
            except Exception as e:
                print(f"⚠️  Monitoring error: {e}")
            
            time.sleep(1)  # Monitor every second
    
    def measure_startup_time(self, compose_file: str = "docker-compose.mvp.yml") -> Dict[str, Any]:
        """Measure application startup time with detailed breakdown"""
        print(f"⏱️  Measuring startup time for {compose_file}...")
        
        startup_metrics = {
            'compose_file': compose_file,
            'hardware_type': self.hardware_info['ml_acceleration'],
            'phases': {},
            'total_time': 0,
            'success': False
        }
        
        try:
            # Phase 1: Docker build/start
            start_time = time.time()
            build_start = time.time()
            
            result = subprocess.run([
                'docker-compose', '-f', compose_file, 'build'
            ], cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                startup_metrics['error'] = f"Build failed: {result.stderr}"
                return startup_metrics
            
            build_time = time.time() - build_start
            startup_metrics['phases']['build'] = build_time
            
            # Phase 2: Container startup
            container_start = time.time()
            
            result = subprocess.run([
                'docker-compose', '-f', compose_file, 'up', '-d'
            ], cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                startup_metrics['error'] = f"Container startup failed: {result.stderr}"
                return startup_metrics
            
            container_time = time.time() - container_start
            startup_metrics['phases']['container_startup'] = container_time
            
            # Phase 3: Service readiness
            readiness_start = time.time()
            readiness_time = self.wait_for_services_ready()
            startup_metrics['phases']['service_readiness'] = readiness_time
            
            # Phase 4: ML model loading (if applicable)
            ml_start = time.time()
            ml_loading_time = self.measure_ml_model_loading()
            startup_metrics['phases']['ml_model_loading'] = ml_loading_time
            
            total_time = time.time() - start_time
            startup_metrics['total_time'] = total_time
            startup_metrics['success'] = True
            
            # Adjust thresholds based on hardware
            thresholds = self.get_startup_thresholds()
            startup_metrics['thresholds'] = thresholds
            startup_metrics['within_threshold'] = total_time <= thresholds['max_startup_time']
            
        except subprocess.TimeoutExpired:
            startup_metrics['error'] = "Startup timed out"
        except Exception as e:
            startup_metrics['error'] = f"Startup measurement failed: {e}"
        
        self.metrics['startup_metrics'] = startup_metrics
        return startup_metrics
    
    def measure_memory_usage(self, compose_file: str = "docker-compose.mvp.yml") -> Dict[str, Any]:
        """Measure memory usage with hardware-aware thresholds"""
        print(f"💾 Measuring memory usage for {compose_file}...")
        
        memory_metrics = {
            'compose_file': compose_file,
            'hardware_type': self.hardware_info['ml_acceleration'],
            'baseline_memory': self.get_baseline_memory(),
            'container_memory': {},
            'total_memory_usage': 0,
            'memory_efficiency': 0,
            'success': False
        }
        
        try:
            # Get container memory usage
            result = subprocess.run([
                'docker', 'stats', '--no-stream', '--format', 'json'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                container_stats = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            stats = json.loads(line)
                            container_stats.append(stats)
                        except json.JSONDecodeError:
                            continue
                
                total_memory = 0
                for container in container_stats:
                    container_name = container.get('Name', 'unknown')
                    memory_usage = self.parse_memory_string(container.get('MemUsage', '0B'))
                    
                    memory_metrics['container_memory'][container_name] = {
                        'usage': memory_usage,
                        'percentage': container.get('MemPerc', '0%').replace('%', ''),
                        'limit': self.parse_memory_string(container.get('MemLimit', '0B'))
                    }
                    
                    total_memory += memory_usage
                
                memory_metrics['total_memory_usage'] = total_memory
                memory_metrics['success'] = True
                
                # Calculate memory efficiency
                total_system_memory = self.hardware_info['memory_total']
                memory_metrics['memory_efficiency'] = (total_memory / total_system_memory) * 100
                
                # Check against hardware-aware thresholds
                thresholds = self.get_memory_thresholds()
                memory_metrics['thresholds'] = thresholds
                memory_metrics['within_threshold'] = total_memory <= thresholds['max_memory_usage']
                
        except Exception as e:
            memory_metrics['error'] = f"Memory measurement failed: {e}"
        
        self.metrics['memory_metrics'] = memory_metrics
        return memory_metrics
    
    def measure_ml_model_loading(self) -> float:
        """Measure ML model loading time"""
        print("🤖 Measuring ML model loading time...")
        
        start_time = time.time()
        
        try:
            # Test ML model loading via API
            import requests
            
            # Wait for API to be ready
            max_wait = 60
            wait_time = 0
            while wait_time < max_wait:
                try:
                    response = requests.get("http://localhost:8000/health", timeout=5)
                    if response.status_code == 200:
                        break
                except:
                    pass
                time.sleep(2)
                wait_time += 2
            
            if wait_time >= max_wait:
                return 0
            
            # Test model loading
            response = requests.get("http://localhost:8000/api/models", timeout=30)
            if response.status_code == 200:
                models = response.json()
                if models:
                    # Test inference to ensure model is loaded
                    test_response = requests.post(
                        "http://localhost:8000/api/infer/image",
                        files={'file': ('test.png', b'fake_image_data', 'image/png')},
                        timeout=30
                    )
                    # Don't fail if inference fails, just measure loading time
            
        except Exception as e:
            print(f"⚠️  ML model loading test failed: {e}")
        
        return time.time() - start_time
    
    def wait_for_services_ready(self, timeout: int = 120) -> float:
        """Wait for services to be ready and return wait time"""
        start_time = time.time()
        
        services = [
            "http://localhost:8000/health",  # Backend
            "http://localhost:3000",         # Frontend
        ]
        
        for service_url in services:
            wait_time = 0
            while wait_time < timeout:
                try:
                    import requests
                    response = requests.get(service_url, timeout=5)
                    if response.status_code == 200:
                        break
                except:
                    pass
                time.sleep(2)
                wait_time += 2
            
            if wait_time >= timeout:
                print(f"⚠️  Service {service_url} not ready after {timeout}s")
        
        return time.time() - start_time
    
    def get_baseline_memory(self) -> int:
        """Get baseline memory usage before starting containers"""
        return psutil.virtual_memory().used
    
    def parse_memory_string(self, memory_str: str) -> int:
        """Parse memory string like '123.4MiB' to bytes"""
        if not memory_str or memory_str == '0B':
            return 0
        
        memory_str = memory_str.replace('B', '').replace('i', '')
        
        if 'GiB' in memory_str:
            return int(float(memory_str.replace('GiB', '')) * 1024 * 1024 * 1024)
        elif 'MiB' in memory_str:
            return int(float(memory_str.replace('MiB', '')) * 1024 * 1024)
        elif 'KiB' in memory_str:
            return int(float(memory_str.replace('KiB', '')) * 1024)
        else:
            return int(float(memory_str))
    
    def get_startup_thresholds(self) -> Dict[str, int]:
        """Get hardware-aware startup time thresholds"""
        base_thresholds = {
            'cpu': 120,      # 2 minutes for CPU-only
            'gpu': 180,      # 3 minutes for GPU (model loading)
        }
        
        # Adjust based on hardware capabilities
        if self.hardware_info['gpu_available']:
            base_time = base_thresholds['gpu']
            # Adjust based on GPU memory
            gpu_memory = self.hardware_info['gpu_info'].get('memory_total', 0)
            if gpu_memory < 4000:  # Less than 4GB
                base_time += 60  # Add 1 minute for slower GPU
        else:
            base_time = base_thresholds['cpu']
            # Adjust based on CPU cores
            cpu_cores = self.hardware_info['cpu_count']
            if cpu_cores < 4:
                base_time += 60  # Add 1 minute for fewer cores
        
        return {
            'max_startup_time': base_time,
            'build_time_limit': base_time * 0.4,  # 40% for build
            'container_startup_limit': base_time * 0.2,  # 20% for container startup
            'service_readiness_limit': base_time * 0.3,  # 30% for service readiness
            'ml_loading_limit': base_time * 0.1,  # 10% for ML loading
        }
    
    def get_memory_thresholds(self) -> Dict[str, int]:
        """Get hardware-aware memory usage thresholds"""
        total_memory = self.hardware_info['memory_total']
        
        # Base thresholds as percentage of total memory
        if self.hardware_info['gpu_available']:
            # GPU environments need more memory for models
            max_percentage = 0.8  # 80% of total memory
        else:
            # CPU-only environments
            max_percentage = 0.6  # 60% of total memory
        
        max_memory = int(total_memory * max_percentage)
        
        return {
            'max_memory_usage': max_memory,
            'warning_threshold': int(max_memory * 0.8),  # 80% of max
            'critical_threshold': int(max_memory * 0.95),  # 95% of max
        }
    
    def run_comprehensive_metrics(self, compose_file: str = "docker-compose.mvp.yml") -> Dict[str, Any]:
        """Run comprehensive metrics collection"""
        print(f"📊 Running comprehensive metrics for {compose_file}...")
        
        # Start monitoring
        self.start_monitoring()
        
        try:
            # Measure startup time
            startup_metrics = self.measure_startup_time(compose_file)
            
            # Measure memory usage
            memory_metrics = self.measure_memory_usage(compose_file)
            
            # Collect ML model metrics
            ml_metrics = self.collect_ml_model_metrics()
            
            # Collect build metrics
            build_metrics = self.collect_build_metrics(compose_file)
            
            # Compile results
            self.metrics.update({
                'startup_metrics': startup_metrics,
                'memory_metrics': memory_metrics,
                'ml_model_metrics': ml_metrics,
                'build_metrics': build_metrics
            })
            
            # Generate summary
            summary = self.generate_metrics_summary()
            self.metrics['summary'] = summary
            
            return self.metrics
            
        finally:
            # Stop monitoring
            self.stop_monitoring()
    
    def collect_ml_model_metrics(self) -> Dict[str, Any]:
        """Collect ML model specific metrics"""
        ml_metrics = {
            'models_loaded': 0,
            'model_sizes': {},
            'inference_times': {},
            'gpu_utilization': 0,
            'memory_efficiency': 0
        }
        
        try:
            import requests
            
            # Get model information
            response = requests.get("http://localhost:8000/api/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                ml_metrics['models_loaded'] = len(models)
                
                for model in models:
                    model_name = model.get('name', 'unknown')
                    model_size = model.get('size', 0)
                    ml_metrics['model_sizes'][model_name] = model_size
                    
                    # Test inference time
                    inference_time = self.measure_inference_time(model_name)
                    ml_metrics['inference_times'][model_name] = inference_time
            
            # Get GPU utilization if available
            if self.hardware_info['gpu_available']:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        ml_metrics['gpu_utilization'] = gpus[0].load * 100
                except:
                    pass
            
        except Exception as e:
            ml_metrics['error'] = f"ML metrics collection failed: {e}"
        
        return ml_metrics
    
    def measure_inference_time(self, model_name: str) -> float:
        """Measure inference time for a specific model"""
        try:
            import requests
            import io
            from PIL import Image
            
            # Create test image
            img = Image.new('RGB', (224, 224), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/api/infer/image",
                files={'file': ('test.png', img_bytes.getvalue(), 'image/png')},
                timeout=30
            )
            return time.time() - start_time
            
        except Exception as e:
            return 0.0
    
    def collect_build_metrics(self, compose_file: str) -> Dict[str, Any]:
        """Collect build-specific metrics"""
        build_metrics = {
            'compose_file': compose_file,
            'build_time': 0,
            'image_sizes': {},
            'layer_count': 0,
            'build_efficiency': 0
        }
        
        try:
            # Get Docker image information
            result = subprocess.run([
                'docker', 'images', '--format', 'json'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                total_size = 0
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            image_info = json.loads(line)
                            image_name = image_info.get('Repository', 'unknown')
                            image_size = int(image_info.get('Size', '0').replace('MB', '').replace('GB', ''))
                            build_metrics['image_sizes'][image_name] = image_size
                            total_size += image_size
                        except:
                            continue
                
                build_metrics['total_image_size'] = total_size
                build_metrics['build_efficiency'] = self.calculate_build_efficiency(total_size)
        
        except Exception as e:
            build_metrics['error'] = f"Build metrics collection failed: {e}"
        
        return build_metrics
    
    def calculate_build_efficiency(self, total_size: int) -> float:
        """Calculate build efficiency score"""
        # Efficiency based on total image size
        if total_size < 1000:  # Less than 1GB
            return 1.0
        elif total_size < 2000:  # Less than 2GB
            return 0.8
        elif total_size < 5000:  # Less than 5GB
            return 0.6
        else:
            return 0.4
    
    def generate_metrics_summary(self) -> Dict[str, Any]:
        """Generate comprehensive metrics summary"""
        summary = {
            'overall_status': 'PASS',
            'hardware_type': self.hardware_info['ml_acceleration'],
            'performance_score': 0,
            'efficiency_score': 0,
            'recommendations': []
        }
        
        # Calculate performance score
        startup_ok = self.metrics['startup_metrics'].get('within_threshold', False)
        memory_ok = self.metrics['memory_metrics'].get('within_threshold', False)
        
        performance_score = 0
        if startup_ok:
            performance_score += 50
        if memory_ok:
            performance_score += 50
        
        summary['performance_score'] = performance_score
        
        # Calculate efficiency score
        memory_efficiency = self.metrics['memory_metrics'].get('memory_efficiency', 0)
        build_efficiency = self.metrics['build_metrics'].get('build_efficiency', 0)
        
        efficiency_score = (memory_efficiency + build_efficiency * 100) / 2
        summary['efficiency_score'] = efficiency_score
        
        # Generate recommendations
        if not startup_ok:
            summary['recommendations'].append({
                'type': 'performance',
                'priority': 'high',
                'message': 'Startup time exceeds thresholds. Consider optimizing build process or reducing model complexity.'
            })
        
        if not memory_ok:
            summary['recommendations'].append({
                'type': 'memory',
                'priority': 'high',
                'message': 'Memory usage exceeds thresholds. Consider using smaller models or optimizing memory usage.'
            })
        
        if efficiency_score < 70:
            summary['recommendations'].append({
                'type': 'efficiency',
                'priority': 'medium',
                'message': 'System efficiency is low. Consider optimizing resource usage.'
            })
        
        # Determine overall status
        if performance_score < 50 or efficiency_score < 50:
            summary['overall_status'] = 'FAIL'
        elif performance_score < 80 or efficiency_score < 70:
            summary['overall_status'] = 'WARNING'
        
        return summary
    
    def save_metrics(self):
        """Save metrics to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        metrics_file = self.metrics_dir / f'metrics_{timestamp}.json'
        
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        # Also save latest metrics
        latest_file = self.metrics_dir / 'latest_metrics.json'
        with open(latest_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"💾 Metrics saved to: {metrics_file}")
    
    def print_summary(self):
        """Print metrics summary"""
        summary = self.metrics.get('summary', {})
        
        print(f"\n📊 AL-0 Automated Metrics Summary")
        print(f"Hardware Type: {summary.get('hardware_type', 'unknown').upper()}")
        print(f"Overall Status: {summary.get('overall_status', 'UNKNOWN')}")
        print(f"Performance Score: {summary.get('performance_score', 0)}/100")
        print(f"Efficiency Score: {summary.get('efficiency_score', 0)}/100")
        
        # Startup metrics
        startup = self.metrics.get('startup_metrics', {})
        if startup.get('success'):
            print(f"\n⏱️  Startup Time: {startup.get('total_time', 0):.2f}s")
            print(f"   Build: {startup.get('phases', {}).get('build', 0):.2f}s")
            print(f"   Container: {startup.get('phases', {}).get('container_startup', 0):.2f}s")
            print(f"   Services: {startup.get('phases', {}).get('service_readiness', 0):.2f}s")
            print(f"   ML Loading: {startup.get('phases', {}).get('ml_model_loading', 0):.2f}s")
        
        # Memory metrics
        memory = self.metrics.get('memory_metrics', {})
        if memory.get('success'):
            total_mb = memory.get('total_memory_usage', 0) / (1024 * 1024)
            print(f"\n💾 Memory Usage: {total_mb:.2f} MB")
            print(f"   Efficiency: {memory.get('memory_efficiency', 0):.1f}%")
        
        # ML metrics
        ml = self.metrics.get('ml_model_metrics', {})
        print(f"\n🤖 ML Models: {ml.get('models_loaded', 0)} loaded")
        if ml.get('gpu_utilization', 0) > 0:
            print(f"   GPU Utilization: {ml.get('gpu_utilization', 0):.1f}%")
        
        # Recommendations
        recommendations = summary.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                print(f"   {priority_icon} {rec['message']}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AL-0 Automated Metrics Tracker')
    parser.add_argument('--compose-file', default='docker-compose.mvp.yml',
                       help='Docker compose file to test')
    parser.add_argument('--save', action='store_true',
                       help='Save metrics to file')
    
    args = parser.parse_args()
    
    tracker = AutomatedMetricsTracker()
    
    print(f"🚀 Starting automated metrics tracking...")
    print(f"Hardware: {tracker.hardware_info['ml_acceleration'].upper()}")
    print(f"GPU Available: {tracker.hardware_info['gpu_available']}")
    
    # Run comprehensive metrics
    metrics = tracker.run_comprehensive_metrics(args.compose_file)
    
    # Print summary
    tracker.print_summary()
    
    # Save if requested
    if args.save:
        tracker.save_metrics()
    
    # Exit with error code if metrics failed
    summary = metrics.get('summary', {})
    if summary.get('overall_status') == 'FAIL':
        exit(1)
    else:
        exit(0)

if __name__ == '__main__':
    main()
